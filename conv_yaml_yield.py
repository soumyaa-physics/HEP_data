import yaml
import argparse
import os

class FlowStyleList(list):
    pass

def flow_style_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowStyleList, flow_style_list_representer)

parser = argparse.ArgumentParser(description="Convert yield plots")
parser.add_argument("input_file", help="Path to the raw YAML file")
parser.add_argument("-o", "--output_dir", default=".", help="Directory to save the single YAML file")
args = parser.parse_args()

input_path = args.input_file
output_dir = args.output_dir

with open(input_path) as f:
    raw = yaml.safe_load(f)

eras = list(raw.keys())             
categories = list(raw[eras[0]].keys()) 

def get_sorted_bins(cat_dict):
    bin_keys = [k for k, v in cat_dict.items() if isinstance(v, dict)]
    
    def sort_key(x):
        try:
            return (0, int(x))
        except ValueError:
            return (1, str(x)) 
    
    return sorted(bin_keys, key=sort_key)

tables = []

for category in categories:
    if not all(isinstance(raw[era][category], dict) for era in eras):
        continue

    bins = get_sorted_bins(raw[eras[0]][category])

    independent_variables = [{
        "header": {"name": "Bin", "units": ""},
        "values": [{"value": str(b)} for b in bins]
    }]

#should be like this:  - {symerror: 79, label: 'sys,detector'} - {symerror: 15, label: 'sys,background'}
    dependent_variables = []
    for era in eras:
        dep_values = []
        for b in bins:
            bin_data = raw[era][category][b]
            errors = []

            # Statistical uncertainty
            if "unc_stat" in bin_data:
                errors.append({"symerror": bin_data["unc_stat"], "label": "stat"})

            # Systematic uncertainty
            if "unc_syst" in bin_data:
                errors.append({"symerror": bin_data["unc_syst"], "label": "syst"})

            dep_values.append({
                "value": bin_data["yield"],
                "errors": FlowStyleList(errors)
            })

    dependent_variables.append({
        "header": {"name": f"Yield_{era}", "units": ""},
        "values": dep_values
    })
    tables.append({
        "name": category,
        "independent_variables": independent_variables,
        "dependent_variables": dependent_variables
    })

hepdata_output = {"tables": tables}

output_filename = os.path.splitext("HEP_yield_" + os.path.basename(input_path))[0] + ".yaml"
output_path = os.path.join(output_dir, output_filename)

with open(output_path, "w") as f:
    yaml.dump(hepdata_output, f, sort_keys=False)

print(f"Converted {input_path} → {output_path} (all categories in one file)")

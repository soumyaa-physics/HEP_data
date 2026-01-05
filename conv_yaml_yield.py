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
# parser.add_argument("-o", "--output_dir", default=".", help="Directory to save the single YAML file")
args = parser.parse_args()

input_path = args.input_file
output_dir = "./Figure4,5,6"

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

figure_metadata = {
    "name": "Figure 6a (prefit yields)",
    "description": (
        "Observed and predicted event yields in the eight SR bins as defined in Table 2 "
        "The signal distributions yields in the maximally mixed scenario for a few "
        "representative sets of $(m_{\\tilde{\\tau}} [\\text{GeV}], c\\tau_{0} [\\text{mm}])$ "
        "values are overlaid: (100, 50), (100, 100), (200, 50), and (200, 100). "
        "The predicted yields and uncertainties are before the maximum likelihood fit to data "
        "under the background-only hypothesis, as described in Section 8. "
        # "In bins where the observed yield is zero, the Poissonian upper limit at 68% CL "
        # "is shown as a positive uncertainty. The last bin includes the overflow."
    ),
    "keywords": [{"name": "cmenergies", "values": [13000.0]}],
    "data_file": "hepdata_Figure6a.yaml"
}

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
                "errors": errors
            })

    dependent_variables.append({
        "header": {"name": f"Yield_{era}", "units": ""},
        "values": dep_values
    })

    table = {
        "name": category,
        "dependent_variables": dependent_variables,
        "independent_variables": independent_variables,
        "description": f"Yields for {category}",
        "keywords": figure_metadata["keywords"],
    }
    tables.append(table)

output_filename = os.path.splitext(os.path.basename(input_path))[0] + ".yaml"
output_path = os.path.join(output_dir, output_filename)

# with open(output_path, "w") as f:
#     yaml.dump(hepdata_output, f, sort_keys=False)
with open(output_path, "w") as f_out:
    # Write figure-level metadata first
    yaml.dump({
        "name": figure_metadata["name"],
        "description": figure_metadata["description"],
        "keywords": figure_metadata["keywords"],
        "data_file": figure_metadata["data_file"]
    }, f_out, sort_keys=False)
    f_out.write("\n")

    # Then append tables
    for table in tables:
        table_to_dump = {
            "dependent_variables": table["dependent_variables"],
            "independent_variables": table["independent_variables"],
            "description": table.get("description", ""),
            "keywords": table.get("keywords", []),
            "name": table.get("name", ""),
        }
        yaml.dump(table_to_dump, f_out, sort_keys=False)
        f_out.write("\n")  # separate multiple tables if needed

print(f"Converted {input_path} → {output_path} (all methods in one file)")

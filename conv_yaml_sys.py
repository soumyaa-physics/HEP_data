import yaml
import argparse
import os

parser = argparse.ArgumentParser(description="Convert nested raw YAML to a single HEPData-style YAML file with all methods as tables")
parser.add_argument("input_file", help="Path to the raw YAML file")
parser.add_argument("-o", "--output_dir", default=".", help="Directory to save the single YAML file")
args = parser.parse_args()

input_path = args.input_file
output_dir = args.output_dir

with open(input_path) as f:
    raw = yaml.safe_load(f)

eras = list(raw.keys())  
category = list(raw[eras[0]].keys())[0]  
methods = list(raw[eras[0]][category].keys())

def get_sorted_bins(method_dict):
    bin_keys = [k for k, v in method_dict.items() if isinstance(v, dict)]
    try:
        return sorted(bin_keys, key=lambda x: int(x))
    except Exception:
        return sorted(bin_keys)

tables = []

for method in methods:
    if not all(isinstance(raw[era][category][method], dict) for era in eras):
        continue

    bins = get_sorted_bins(raw[eras[0]][category][method])

    independent_variables = [{
        "header": {"name": "Bin", "units": ""},
        "values": [{"value": int(b)} for b in bins]
    }]

    dependent_variables = []
    for era in eras:
        dep_values = []
        for b in bins:
            bin_data = raw[era][category][method][b]
            if all(k in bin_data for k in ("yield", "unc_abs", "unc_rel")):
                dep_values.append({
                    "value": bin_data["yield"],
                    "errors": [
                        {"symerror": bin_data["unc_abs"], "label": "unc_abs"},
                        {"symerror": bin_data["unc_rel"], "label": "unc_rel"}
                    ]
                })
            else:
                dep_values.append({"value": None, "errors": []})
        dependent_variables.append({
            "header": {"name": f"Yield_{era}", "units": ""},
            "values": dep_values
        })

    tables.append({
        "name": method,
        "independent_variables": independent_variables,
        "dependent_variables": dependent_variables
    })

hepdata_output = {"tables": tables}

output_filename = os.path.splitext(os.path.basename(input_path))[0] + "_allmethods_hepdata.yaml"
output_path = os.path.join(output_dir, output_filename)

with open(output_path, "w") as f:
    yaml.dump(hepdata_output, f, sort_keys=False)

print(f"Converted {input_path} → {output_path} (all methods in one file)")

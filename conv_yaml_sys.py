import yaml
import argparse
import os

parser = argparse.ArgumentParser(description="Convert systematic uncertainties")
parser.add_argument("input_file", help="Path to the raw YAML file")

args = parser.parse_args()

input_path = args.input_file
output_dir = "./Figure3"

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

# figure_metadata = {
#     "name": "Figure 3",
#     "description": (
#         "DISTAU classifier distributions for τh probes in the μτh control region (2018). "
#         "DY(μτh) denotes Z/γ* → ττ events with one tau → μ and the other hadronic "
#         "DY(other) includes other Z/γ* decays. 'Top quark' includes tt, single top, ttV "
#         "other SM processes include diboson. Grey band: statistical uncertainty on simulation. "
#         "Simulation is illustrative; not fully calibrated or used for correction factors. "
#         "2016/2017 data show similar behavior."
#     ),
#     "keywords": [{"name": "cmenergies", "values": [13000.0]}],
#     "data_file": "hepdata_Figure3.yaml"
# }

for method in methods:
    if not all(isinstance(raw[era][category][method], dict) for era in eras):
        continue

    bins = get_sorted_bins(raw[eras[0]][category][method])

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

    independent_variables = [{
        "header": {"name": "Bin", "units": ""},
        "values": [{"value": int(b)} for b in bins]
    }]

        # Create table dictionary and append to tables
    table = {
        "name": method,
        "dependent_variables": dependent_variables,
        "independent_variables": independent_variables,
        "description": f"Yields for method {method}"
    }
    tables.append(table)

outname = "hepdata_Table3.yaml"

with open(outname, "w") as f_out:
    # # Write figure-level metadata first
    # yaml.dump({
    #     "name": figure_metadata["name"],
    #     "description": figure_metadata["description"],
    #     "keywords": figure_metadata["keywords"],
    #     "data_file": figure_metadata["data_file"]
    # }, f_out, sort_keys=False)
    # f_out.write("\n")

    # Then append tables
    for table in tables:
        table_to_dump = {
            "dependent_variables": table["dependent_variables"],
            "independent_variables": table["independent_variables"],
        #     "description": table.get("description", ""),
        #     "keywords": table.get("keywords", []),
        #     "name": table.get("name", ""),
        }
        yaml.dump(table_to_dump, f_out, sort_keys=False)
        f_out.write("\n")  # separate multiple tables if needed

print(f"Converted {input_path} → {outname} (all methods in one file)")
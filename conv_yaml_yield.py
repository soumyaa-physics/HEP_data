import yaml
import argparse
import os
import re
import math

parser = argparse.ArgumentParser(description="Convert yield YAML to HEPData format")
parser.add_argument("input_file")
args = parser.parse_args()

input_path = args.input_file
output_dir = "./HEPdata"
os.makedirs(output_dir, exist_ok=True)

BIN_EDGES = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
# BIN_EDGES = [0.0, 54.0, 102.0, 150.0, 204.0, 300.0]

X_AXIS_LABEL =  "$SR bins$"
X_AXIS_UNITS = ""
Y_AXIS_LABEL = "Events"
outname = os.path.join(output_dir, "hepdata_Figure6a.yaml")

def make_bin_ranges(edges):
    return [{"low": edges[i], "high": edges[i+1]}
            for i in range(len(edges) - 1)]

def fmt(x):
    return float(f"{x:0.6g}")

def get_sorted_bins(proc_dict):
    bins = []
    for k in proc_dict:
        if k == "total":
            continue
        try:
            bins.append(int(k))
        except ValueError:
            pass
    return sorted(bins)


def format_process_name(name):

    if name == "obs":
        return "Data"

    if name == "total_bkg":
        return "Total background"

    m = re.search(r"MStau-(\d+).*ctau-(\d+)mm", name)
    if m:
        mass = m.group(1)
        ctau = m.group(2)
        return f"$m_{{\\tilde{{\\tau}}}}={mass}$ GeV, $c\\tau_0={ctau}$ mm"

    return name

with open(input_path) as f:
    raw = yaml.safe_load(f)

era_key = list(raw.keys())[0]
era_block = raw[era_key]


bin_ranges = make_bin_ranges(BIN_EDGES)

# defining variables:

independent_variables = [{
    "header": {
        "name": X_AXIS_LABEL,
        "units": X_AXIS_UNITS
    },
    "values": bin_ranges
}]

dependent_variables = []

for process_name, proc_dict in era_block.items():

    if not isinstance(proc_dict, dict):
        continue

    if process_name == "misid":
        continue

    bins = get_sorted_bins(proc_dict)
    is_data = (process_name == "obs")

    dep_values = []
    for b in bins:

        bin_data = proc_dict.get(b, proc_dict.get(str(b)))        
        value = fmt(bin_data["yield"])

        errors = []
        if is_data:
            if value > 0.0:
                data_stat = fmt(math.sqrt(value))
                errors.append({
                    "label": "Statistical",
                    "symerror": data_stat
                })

            else:
                plus = fmt(bin_data.get("unc_stat_plus", 1.83258))
                minus = fmt(bin_data.get("unc_stat_minus", 0.0))

                errors.append({
                    "label": "Statistical",
                    "asymerror": {
                        "minus": minus,
                        "plus": plus
                    }
                    })

        else: 
            if "unc_stat" in bin_data:
                errors.append({
                    "label": "Statistical",
                    "symerror": fmt(bin_data["unc_stat"])
                })

            if "unc_syst" in bin_data:
                errors.append({
                    "label": "Systematic",
                    "symerror": fmt(bin_data["unc_syst"])
                })

        dep_values.append({
            "value": fmt(bin_data["yield"]),
            "errors": errors
        })
        
    dependent_variables.append({
        "header": {
            "name": Y_AXIS_LABEL
        },
        "qualifiers": [
            {
                "name": "Process",
                "value": format_process_name(process_name)
            }
        ],
        "values": dep_values
    })


table = {
    "dependent_variables": dependent_variables,
    "independent_variables": independent_variables

}


with open(outname, "w") as f_out:
    yaml.dump(table, f_out, sort_keys=False)

print(f"Written HEPData file: {outname}")
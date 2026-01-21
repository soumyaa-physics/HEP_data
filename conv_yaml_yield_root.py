import yaml
import ROOT
import ctypes
import argparse
import os
import math

parser = argparse.ArgumentParser(description="Convert yield ROOT to HEPData format")
parser.add_argument("input_file", help="Path to the ROOT file")
args = parser.parse_args()

input_path = args.input_file
output_dir = "./HEPdata"
os.makedirs(output_dir, exist_ok=True)

BIN_EDGES = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

X_AXIS_LABEL = "$SR bins$"
X_AXIS_UNITS = ""
Y_AXIS_LABEL = "Events"

outname = os.path.join(output_dir, "hepdata_Figure6b.yaml")

f = ROOT.TFile.Open(input_path)

def make_bin_ranges(edges):
    return [{"low": edges[i], "high": edges[i+1]}
            for i in range(len(edges)-1)]

def fmt(x):
    return float(f"{x:.6g}")

bin_ranges = make_bin_ranges(BIN_EDGES)

independent_variables = [{
    "header": {
        "name": X_AXIS_LABEL,
        "units": X_AXIS_UNITS
    },
    "values": bin_ranges
}]

graphs = {
    "postfit_data_obs": {
        "path": "BRT2_added_postfit_data_obs",
        "process": "Data"
    },
    "postfit_misid": {
        "path": "BRT2_added_postfit_misid",
        "process": "Total Background"
    },
}

dependent_variables = []


for key, info in graphs.items():

    process_name = info["process"]

    # Skip misid (same as YAML version)
    if process_name == "misid":
        continue

    hist = f.Get(info["path"])
    if not hist:
        raise RuntimeError(f"Missing histogram: {info['path']}")

    n_bins = hist.GetNbinsX()

    is_data = (process_name == "Data")

    dep_values = []

    for i in range(1, n_bins + 1):

        value = fmt(hist.GetBinContent(i))

        errors = []

        # ---------- DATA ----------
        if is_data:

            if value > 0.0:
                stat = fmt(math.sqrt(value))
                errors.append({
                    "label": "Statistical",
                    "symerror": stat
                })

            else:
                # one-sided Poisson convention
                errors.append({
                    "label": "Statistical",
                    "asymerror": {
                        "minus": 0.0,
                        "plus": 1.83258
                    }
                })

        # ---------- BACKGROUND ----------
        else:

            stat_err = hist.GetBinError(i)

            if stat_err > 0:
                errors.append({
                    "label": "Statistical",
                    "symerror": fmt(stat_err)
                })

        dep_values.append({
            "value": value,
            "errors": errors
        })

    dependent_variables.append({
        "header": {
            "name": Y_AXIS_LABEL
        },
        "qualifiers": [
            {
                "name": "Process",
                "value": process_name
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
import yaml
import ROOT
import ctypes
import argparse
import os

class FlowStyleList(list):
    pass

def flow_style_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowStyleList, flow_style_list_representer)

parser = argparse.ArgumentParser(description="Convert yield plots")
parser.add_argument("input_file", help="Path to the ROOT file")
# parser.add_argument("-o", "--output_dir", default=".", help="Directory to save the single YAML file")
args = parser.parse_args()

input_path = args.input_file
output_dir = "./EXO-24-020_HEPData/HEPdata/Figure4,5,6"

f = ROOT.TFile(input_path)

graphs = {
    "postfit_misid": {
        "path": "BRT2_added_postfit_misid",
        "description": "Postfit misidentified events",
    },
    "postfit_data_obs": {
        "path": "BRT2_added_postfit_data_obs",
        "description": "Postfit observed data",
    },
}


tables = []

figure_metadata = {
    "name": "Figure 6b (postfit yields)",
    "description": (
        "Observed and predicted event yields in the eight SR bins as defined in Table 2 "
        "The signal distributions yields in the maximally mixed scenario for a few "
        "representative sets of $(m_{\\tilde{\\tau}} [\\text{GeV}], c\\tau_{0} [\\text{mm}])$ "
        "values are overlaid: (100, 50), (100, 100), (200, 50), and (200, 100). "
        "The predicted yields and uncertainties are after the maximum likelihood fit to data "
        "under the background-only hypothesis, as described in Section 8. "
        # "In bins where the observed yield is zero, the Poissonian upper limit at 68% CL "
        # "is shown as a positive uncertainty. The last bin includes the overflow."
    ),
    "keywords": [{"name": "cmenergies", "values": [13000.0]}],
    "data_file": "hepdata_Figure6b.yaml"
}


for label, info in graphs.items():
    graph = f.Get(info["path"])
    if not graph:
        print(f"NOT FOUND: {info['path']}")
        continue

    n_bins = graph.GetNbinsX()
    x_vals = [graph.GetBinCenter(i) for i in range(1, n_bins+1)]
    z_vals = [graph.GetBinContent(i) for i in range(1, n_bins+1)]

    indep_vars = [
        {"header": {"name": "Bin", "units": ""}, 
         "values": [{"value": str(int(b))} for b in x_vals]}
    ]

    dep_vars = [
        {
            "header": {"name": info["description"]},
            "values": [{"value": zv, "errors": FlowStyleList([])} for zv in z_vals]
        }
    ]

    table = {
        "name": label,
        "description": info["description"],
        "keywords": figure_metadata["keywords"],
        "dependent_variables": dep_vars,
        "independent_variables": indep_vars,
    }
    tables.append(table)

# Output YAML
output_filename = os.path.splitext(os.path.basename(input_path))[0] + ".yaml"
output_path = os.path.join(output_dir, output_filename)

with open(output_path, "w") as f_out:
    # Figure-level metadata
    yaml.dump({
        "name": figure_metadata["name"],
        "description": figure_metadata["description"],
        "keywords": figure_metadata["keywords"],
        "data_file": figure_metadata["data_file"]
    }, f_out, sort_keys=False)
    f_out.write("\n")

    # Append tables
    for table in tables:
        yaml.dump(table, f_out, sort_keys=False)
        f_out.write("\n")

print(f"Converted {input_path} → {output_path}")
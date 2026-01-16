import ROOT
import yaml
import ctypes
import os

# for FIGURE 7

input_file = "EXO-24-020_HEPData/data/Figure7a_Figure8_limits.root"
f = ROOT.TFile(input_file)

with open("7adictionary.yaml") as fi:
    table_metadata = yaml.safe_load(fi)

graphs = {
    "observed": {
        "path": "obs/h2_xsecul_obs_interp",
        "description": "2D histogram (color axis)",
        "type": "TH2D"
    },
    "observed_exclusion": {
        "path": "obs/contour_obs",
        "description": "observed exclusion contours",
        "type": "TGraph"
    },
    "obs_minu1sigma": {
        "path": "obs_m1/contour_obs_m1",
        "description": "observed exclusion contours (minus 1 sigma)",
        "type": "TGraph"
    },
    "obs_plus1sigma": {
        "path": "obs_p1/contour_obs_p1",
        "description": "observed exclusion contours (plus 1 sigma)",
        "type": "TGraph"
    },
    "exp_contour": {
        "path": "exp/contour_exp",
        "description": "expected exclusion contours",
        "type": "TGraph"
    },
    "exp_minus1sigma": {
        "path": "exp_m1/contour_exp_m1",
        "description": "expected exclusion contours (minus 1 sigma)",
        "type": "TGraph"
    },
    "exp_minus2sigma": {
        "path": "exp_m2/contour_exp_m2",
        "description": "expected exclusion contours (minus 2 sigma)",
        "type": "TGraph"
    },
    "exp_plus1sigma": {
        "path": "exp_p1/contour_exp_p1",
        "description": "expected exclusion contours (plus 1 sigma)",
        "type": "TGraph"
    },
    "exp_plus2sigma": {
        "path": "exp_p2/contour_exp_p2",
        "description": "expected exclusion contours (plus 2 sigma)",
        "type": "TGraph"
    },    
}

output_dir = "./HEPdata"


for label, info in graphs.items():
    path = info["path"]
    graph_type = info["type"]

    graph = f.Get(path)
    if not graph:
        print(f"NOT FOUND: {path}")
        continue

    # Get metadata for this table
    meta = table_metadata.get(label, {})
    data_file = meta.get("data_file")
    if not data_file:
        raise RuntimeError(f"Missing 'data_file' entry in metadata for {label}")

    x_vals, y_vals, z_vals = [], [], []

    # Extract values depending on graph type
    if graph_type == "TGraph":
        n = graph.GetN()
        x = ctypes.c_double()
        y = ctypes.c_double()
        for i in range(n):
            graph.GetPoint(i, x, y)
            x_vals.append(x.value)
            z_vals.append(y.value)  # TGraph: y-values go into dependent variable
        indep_vars = [{"header": {"name": "m_stau", "units": "GeV"},
                       "values": [{"value": xv} for xv in x_vals]}]
        dep_vars = [{"header": {"name": "95% CL limit"},
                     "qualifiers": [
                         {"name": "RE", "value": "pp → \\tilde{τ}\\tilde{τ}"},
                         {"name": "MODEL", "value": "GMSB maximally mixed  stau scenario"},
                         {"name": "SQRT(S)", "value": "13 TeV"},
                         {"name": "LUMI", "value": "138 fb^{-1}"},
                         {"name": "CL", "value": "95%"},
                     ],
                     "values": [{"value": zv} for zv in z_vals]}]

    elif graph_type == "TH2D":
        n_x = graph.GetNbinsX()
        n_y = graph.GetNbinsY()
        for i in range(1, n_x + 1):
            for j in range(1, n_y + 1):
                x_vals.append(graph.GetXaxis().GetBinCenter(i))
                y_vals.append(graph.GetYaxis().GetBinCenter(j))
                z_vals.append(graph.GetBinContent(i, j))
        indep_vars = [
            {"header": {"name": "Mass of stau", "units": "GeV"}, "values": [{"value": xv} for xv in x_vals]},
            {"header": {"name": "Proper lifetime", "units": "mm"}, "values": [{"value": yv} for yv in y_vals]},
        ]
        dep_vars = [{"header": {"name": "95% CL limit"},
                     "qualifiers": [
                         {"name": "RE", "value": "pp → \\tilde{τ}\\tilde{τ}"},
                         {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
                         {"name": "SQRT(S)", "value": "13 TeV"},
                         {"name": "LUMI", "value": "138 fb^{-1}"},
                         {"name": "CL", "value": "95%"},
                     ],
                     "values": [{"value": zv} for zv in z_vals]}]

    # Write table to its own YAML file (filename = metadata 'data_file')
    outpath = os.path.join(output_dir, data_file)
    with open(outpath, "w") as f_out:
        yaml.dump({"independent_variables": indep_vars,
                   "dependent_variables": dep_vars}, f_out, sort_keys=False)
    print(f"Written table {label} -> {outpath}")
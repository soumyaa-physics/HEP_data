import ROOT
import yaml
import ctypes

f = ROOT.TFile("limits.root")

graphs = {
    "observed": {
        "path": "obs/h2_xsecul_obs_interp",
        "description": "observed exclusion contours",
        "type": "TH2D"
    },
    "contour_obs": {
        "path": "obs/contour_obs",
        "description": "observed exclusion contours",
        "type": "TGraph"
    },
    "contour_obs_m1": {
        "path": "obs_m1/contour_obs_m1",
        "description": "observed exclusion contours (minus 1 sigma)",
        "type": "TGraph"
    },
    "contour_obs_p1": {
        "path": "obs_p1/contour_obs_p1",
        "description": "observed exclusion contours (plus 1 sigma)",
        "type": "TGraph"
    },
    "exp_contour": {
        "path": "exp/contour_exp",
        "description": "expected exclusion contours",
        "type": "TGraph"
    },
    "exp_contour_m1": {
        "path": "exp_m1/contour_exp_m1",
        "description": "expected exclusion contours (minus 1 sigma)",
        "type": "TGraph"
    },
    "exp_contour_m2": {
        "path": "exp_m2/contour_exp_m2",
        "description": "expected exclusion contours (minus 2 sigma)",
        "type": "TGraph"
    },
    "exp_contour_p1": {
        "path": "exp_p1/contour_exp_p1",
        "description": "expected exclusion contours (plus 1 sigma)",
        "type": "TGraph"
    },
    # "exp_contour_p2": {
    #     "path": "exp_p2/contour_exp_p2",
    #     "description": "expected exclusion contours (plus 2 sigma)",
    #     "type": "TGraph"
    # },
}

tables = []

for label, info in graphs.items():
    path = info["path"]
    description = info["description"]
    graph = f.Get(path)
    type = info["type"]

    if not graph:
        print(f"NOT FOUND: {path}")
        continue

    x_vals = []
    y_vals = []
    z_vals = []

    if type == "TH2D":
        n_x = graph.GetNbinsX()
        n_y = graph.GetNbinsY()

        for i in range(1, n_x+1):
            for j in range(1, n_y+1):
                x = graph.GetXaxis().GetBinCenter(i)
                y = graph.GetYaxis().GetBinCenter(j)
                z = graph.GetBinContent(i, j)

                x_vals.append(x)
                y_vals.append(y)
                z_vals.append(z)
        
        table = {
            "name": label,
            "description": description,
            "dependent_variables": [
                {
                    "header": {"name": "95% CL limit"},
                    "qualifiers": [
                        {"name": "RE", "value": "pp → \\tilde{τ}\\tilde{τ}"},
                        {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
                        {"name": "SQRT(S)", "value": "13 TeV"},
                        {"name": "LUMI", "value": "138 fb^{-1}"},
                        {"name": "CL", "value": "95%"},
                    ],
                    "values": [{"value": zv} for zv in z_vals]
                }
            ],
            "independent_variables": [
                {
                    "header": {"name": "mass of stau", "units": "GeV"},
                    "values": [{"value": xv} for xv in x_vals]
                },
                {
                    "header": {"name": "proper lifetime", "units": "mm"},
                    "values": [{"value": yv} for yv in y_vals]
                }
            ]
        }

    elif type == "TGraph":
        n = graph.GetN()

        x = ctypes.c_double()
        z = ctypes.c_double()

        for i in range(n):
            graph.GetPoint(i, x, z)
            x_vals.append(x.value)
            z_vals.append(z.value)
            y_vals.append(None) 

        table = {
            "name": label,
            "description": description,
            "dependent_variables": [
                {
                    "header": {"name": "95% CL limit"},
                    "qualifiers": [
                        {"name": "RE", "value": "pp → \\tilde{τ}\\tilde{τ}"},
                        {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
                        {"name": "SQRT(S)", "value": "13 TeV"},
                        {"name": "LUMI", "value": "138 fb^{-1}"},
                        {"name": "CL", "value": "95%"},
                    ],
                    "values": [{"value": zv} for zv in z_vals]
                }
            ],
            "independent_variables": [
                {
                    "header": {"name": "mass of stau", "units": "GeV"},
                    "values": [{"value": xv} for xv in x_vals]
                },
            ]
        }

    tables.append(table)

outname = f"contour_hepdata_limits.yaml"

with open(outname, "w") as f_out:
    for table in tables:
        table_to_dump = {
        "dependent_variables": table["dependent_variables"],
        "independent_variables": table["independent_variables"],
        "description": table.get("description", ""),
        "keywords": table.get("keywords", []),
        "name": table.get("name", ""),
        }
        yaml.dump(table_to_dump, f_out, sort_keys=False)
        f_out.write("\n")  

print(f"Output written to {outname}")


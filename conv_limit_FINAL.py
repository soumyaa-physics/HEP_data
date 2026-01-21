import ROOT
import argparse
import yaml
import ctypes
import string
import os

# figure 8 and 9:

input_file = "EXO-24-020_HEPData/data/Figure7a_Figure8_limits.root"
f = ROOT.TFile.Open(input_file)

ctau = [10, 30, 50, 100, 200, 300]

def fmt(x):
    return float(f"{x:.6g}")

with open("8dictionary.yaml") as fi:
    table_metadata = yaml.safe_load(fi)

letters = string.ascii_lowercase[:len(ctau)]

output_dir = "./HEPdata"
os.makedirs(output_dir, exist_ok=True)

for idx, c in enumerate(ctau):

    letter = letters[idx]
    outname = os.path.join(output_dir, f"hepdata_Figure8{letter}.yaml")

    graphs = {
        "observed": f"{c}mm/g1_xsecul_obs_{c}mm",
        "expected": f"{c}mm/g1_xsecul_exp_{c}mm",
        "p1":       f"{c}mm/g1_xsecul_exp_p1_{c}mm",
        "m1":       f"{c}mm/g1_xsecul_exp_m1_{c}mm",
        "p2":       f"{c}mm/g1_xsecul_exp_p2_{c}mm",
        "m2":       f"{c}mm/g1_xsecul_exp_m2_{c}mm",
        "theory":   f"{c}mm/g1_xsec_theory_{c}mm"
    }

    g = {k: f.Get(v) for k, v in graphs.items()}

    for k, gr in g.items():
        if not gr:
            raise RuntimeError(f"Missing graph: {graphs[k]}")


    x_vals = []
    x = ctypes.c_double()
    y = ctypes.c_double()

    npoints = g["expected"].GetN()

    for i in range(npoints):
        g["expected"].GetPoint(i, x, y)
        x_vals.append(fmt(x.value))
    
    # bin_edges = x_vals + [x_vals[-1] + (x_vals[-1]-x_vals[-2])]
    last_width = x_vals[-1] - x_vals[-2]
    bin_edges = x_vals + [fmt(x_vals[-1] + last_width)]

    independent_variables = [{
        "header": {
            "name": "m_{\\tilde{\\tau}}",
            "units": "GeV"
        },
        "values": [
            {"low": bin_edges[i], "high": bin_edges[i+1]}
            for i in range(len(x_vals))
        ]
    }]

    dependent_variables = []

    obs_values = []

    for i in range(npoints):
        g["observed"].GetPoint(i, x, y)
        obs_values.append({"value": fmt(y.value)})

    dependent_variables.append({
        "header": {
            "name": "Upper limit on cross section (Observed)",
            "units": "fb"
        },
        "qualifiers": [
            {"name": "QUANTILE", "value": "Observed"},
            {"name": "PROCESS", "value": "pp → stau stau"},
            {"name": "MODEL", "value": "Maximally mixed scenario"},
            {"name": "CTAU", "value": f"{c} mm"},
            {"name": "SQRT(S)", "value": "13 TeV"},
            {"name": "LUMINOSITY", "value": "138 fb^{-1}"},
            {"name": "CL", "value": "95%"}
        ],
        "values": obs_values
    })

    exp_values = []

    for i in range(npoints):

        xp = ctypes.c_double()
        yp = ctypes.c_double()
        xm = ctypes.c_double()
        ym = ctypes.c_double()
        xp2 = ctypes.c_double()
        yp2 = ctypes.c_double()
        xm2 = ctypes.c_double()
        ym2 = ctypes.c_double()

        g["expected"].GetPoint(i, x, y)
        g["p1"].GetPoint(i, xp, yp)
        g["m1"].GetPoint(i, xm, ym)
        g["p2"].GetPoint(i, xp2, yp2)
        g["m2"].GetPoint(i, xm2, ym2)

        central = fmt(y.value)

        exp_values.append({
            "value": central,
            "errors": [
                {
                    "label": "1 sigma",
                    "asymerror": {
                        "minus": fmt(central - float(ym.value)),
                        "plus":  fmt(float(yp.value) - central)
                    }
                },
                {
                    "label": "2 sigma",
                    "asymerror": {
                        "minus": fmt(central - float(ym2.value)),
                        "plus": fmt(float(yp2.value) - central)
                    }
                }
            ]
        })

    dependent_variables.append({
        "header": {
            "name": "Upper limit on cross section (Expected)",
            "units": "fb"
        },
        "qualifiers": [
            {"name": "QUANTILE", "value": "Expected"},
            {"name": "PROCESS", "value": "pp → stau stau"},
            {"name": "MODEL", "value": "Maximally mixed scenario"},
            {"name": "CTAU", "value": f"{c} mm"},
            {"name": "SQRT(S)", "value": "13 TeV"},
            {"name": "LUMINOSITY", "value": "138 fb^{-1}"},
            {"name": "CL", "value": "95%"}
        ],
        "values": exp_values
    })

    theory_values = []

    for i in range(npoints):
        g["theory"].GetPoint(i, x, y)
        theory_values.append({"value": fmt(y.value)})

    dependent_variables.append({
        "header": {
            "name": "Upper limit on cross section (Theory)",
            "units": "fb"
        },
        "qualifiers": [
            {"name": "TYPE", "value": "Theory"},
            {"name": "PROCESS", "value": "pp → stau stau"},
            {"name": "MODEL", "value": "Maximally mixed scenario"},
            {"name": "SQRT(S)", "value": "13 TeV"}
        ],
        "values": theory_values
    })


    table = {
        "dependent_variables": dependent_variables,
        "independent_variables": independent_variables
    }

    with open(outname, "w") as f_out:
        yaml.dump(table, f_out, sort_keys=False)

    print(f"Output written to {outname}")
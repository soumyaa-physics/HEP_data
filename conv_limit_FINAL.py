import ROOT
import argparse
import yaml
import ctypes
import os

input_file = "EXO-24-020_HEPData/data/Figure7a_Figure8_limits.root"
f = ROOT.TFile(input_file)
ctau = [10,30,50,100,200,300]

with open("8dictionary.yaml") as fi:
    table_metadata = yaml.safe_load(fi)

# used for figure 8 and 9

for c in ctau:
    graphs = {
        "observed": f"{c}mm/g1_xsecul_obs_{c}mm",
        # "obs_plus1sigma": f"",
        # "obs_minus1sigma": f"",
        "expected": f"{c}mm/g1_xsecul_exp_{c}mm",
        "p1": f"{c}mm/g1_xsecul_exp_p1_{c}mm",
        "m1": f"{c}mm/g1_xsecul_exp_m1_{c}mm",
        "p2": f"{c}mm/g1_xsecul_exp_p2_{c}mm",
        "m2": f"{c}mm/g1_xsecul_exp_m2_{c}mm",
        "theory": f"{c}mm/g1_xsec_theory_{c}mm"
    }
    g = {k: f.Get(v) for k, v in graphs.items()}
    for k, gr in g.items():
        if not gr:
            raise RuntimeError(f"Missing graph: {graphs[k]}")
    
    x_vals = []
    x = ctypes.c_double()
    y = ctypes.c_double()

    for i in range(g["expected"].GetN()):
        g["expected"].GetPoint(i, x, y)
        x_vals.append(x.value)

    meta = table_metadata.get(c)

    tables = []
    # Observed table
    obs_values = []
    for i in range(g["observed"].GetN()):
        g["observed"].GetPoint(i, x, y)
        obs_values.append({"value": y.value})

    tables.append({
        "name": meta["name"] + "(observed)",
        "description": meta["description"],     
        "data_file": meta["data_file"],
        "keywords": [{"name": "cmenergies", "values": [13000.0]}],
        "dependent_variables": [{
            "header": {"name": "Upper limit on cross section", "units": "fb"},
            "qualifiers": [
                {"name": "Quantile", "value": "Observed"},
                {"name": "RE", "value": "pp -> stau stau"},
                {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
                {"name": "CTAU", "value": f"{c} mm"},
                {"name": "SQRT(S)", "value": "13 TeV"},
                {"name": "LUMINOSITY", "value": "138 fb^{-1}"},
                {"name": "CL", "value": "95%"},
            ],
            "values": obs_values,
        }],
        "independent_variables": [{
            "header": {"name": "m_stau", "units": "GeV"},
            "values": [{"value": xv} for xv in x_vals],
        }],
    })

    # Expected table
    exp_values = []

    for i in range(g["expected"].GetN()):
        yp = ctypes.c_double()
        ym = ctypes.c_double()
        y2p = ctypes.c_double()
        y2m = ctypes.c_double()

        g["expected"].GetPoint(i, x, y)
        g["p1"].GetPoint(i, ctypes.c_double(), yp)
        g["m1"].GetPoint(i, ctypes.c_double(), ym)
        g["p2"].GetPoint(i, ctypes.c_double(), y2p)
        g["m2"].GetPoint(i, ctypes.c_double(), y2m)

        exp_values.append({
            "value": y.value,
            "errors": [
                {
                    "label": "1 s.d.",
                    "asymerror": {
                        "minus": y.value - ym.value,
                        "plus":  yp.value - y.value,
                    },
                },
                {
                    "label": "2 s.d.",
                    "asymerror": {
                        "minus": y.value - y2m.value,
                        "plus":  y2p.value - y.value,
                    },
                },
            ],
        })

    tables.append({
        "name": meta["name"] + "(expected)",
        "description": meta["description"],     
        "data_file": meta["data_file"],
        "keywords": [{"name": "cmenergies", "values": [13000.0]}],
        "dependent_variables": [{
            "header": {"name": "Upper limit on cross section", "units": "fb"},
            "qualifiers": [
                {"name": "Quantile", "value": "Expected"},
                {"name": "RE", "value": "pp -> stau stau"},
                {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
                {"name": "CTAU", "value": f"{c} mm"},
                {"name": "SQRT(S)", "value": "13 TeV"},
                {"name": "LUMINOSITY", "value": "138 fb^{-1}"},
                {"name": "CL", "value": "95%"},
            ],
            "values": exp_values,
        }],
        "independent_variables": [{
            "header": {"name": "m_stau", "units": "GeV"},
            "values": [{"value": xv} for xv in x_vals],
        }],
    })

    # Theory table

    theory_values = []
    for i in range(g["theory"].GetN()):
        g["theory"].GetPoint(i, x, y)
        theory_values.append({"value": y.value})

    tables.append({
        "name": meta["name"] + "(theory)",
        "description": meta["description"],     
        "data_file": meta["data_file"],
        "keywords": [{"name": "cmenergies", "values": [13000.0]}],
        "dependent_variables": [{
            "header": {"name": "Cross section", "units": "fb"},
            "qualifiers": [
                {"name": "TYPE", "value": "Theory"},
                {"name": "RE", "value": "pp -> stau stau"},
                {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
                {"name": "CTAU", "value": f"{c} mm"},
                {"name": "SQRT(S)", "value": "13 TeV"},
            ],
            "values": theory_values,
        }],
        "independent_variables": [{
            "header": {"name": "m_stau", "units": "GeV"},
            "values": [{"value": xv} for xv in x_vals],
        }],
    })

    
    output_dir = "./Figure8"
    outname = os.path.join(output_dir, f"{c}mm_hepdata_limits.yaml")

    with open(outname, "w") as f_out:
        for table in tables:
            # Remove 'name', 'description', 'keywords' from top level for single-table YAML
            table_to_dump = {
                "dependent_variables": table["dependent_variables"],
                "independent_variables": table["independent_variables"],
                "description": table.get("description", ""),
                "keywords": table.get("keywords", []),
                "name": table.get("name", ""),
            }
            yaml.dump(table_to_dump, f_out, sort_keys=False)
            f_out.write("\n")  # separate multiple tables if needed


    print(f"Output written to {outname}")


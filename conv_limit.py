import ROOT
import yaml
import ctypes

f = ROOT.TFile("limits.root")
ctau = [10,30,50,100,200,300]

for c in ctau:
    graphs = {
        "observed": f"{c}mm/g1_xsecul_obs_{c}mm",
        "expected": f"{c}mm/g1_xsecul_exp_{c}mm",
        "exp_plus1sigma": f"{c}mm/g1_xsecul_exp_p1_{c}mm",
        "exp_minus1sigma": f"{c}mm/g1_xsecul_exp_m1_{c}mm",
        "exp_plus2sigma": f"{c}mm/g1_xsecul_exp_p2_{c}mm",
        "exp_minus2sigma": f"{c}mm/g1_xsecul_exp_m2_{c}mm",
        "theory": f"{c}mm/g1_xsec_theory_{c}mm"
    }

    tables = []

    for label, path in graphs.items():
        graph = f.Get(path)
        if not graph:
            print(f"Warning: graph {path} not found")
            continue

        n = graph.GetN()
        x_vals, y_vals = [], []

        for i in range(n):
            x = ctypes.c_double()
            y = ctypes.c_double()
            graph.GetPoint(i, x, y)
            x_vals.append(x.value)
            y_vals.append(y.value)

        table = {
            "name": label,
            "dependent_variables": [
                {"header": {"name": "95% CL limit"},
                "qualifiers": [
            {"name": "RE", "value": "pp → \tilde{τ}\tilde{τ}"},
            {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
            {"name": "CTAU", "value": f"{c} mm"},  # use loop variable
            {"name": "SQRT(S)", "value": "13 TeV"},
            {"name": "LUMI", "value": "138 fb^{-1}"},
            {"name": "CL", "value": "95%"},
            ],
                 "values": [{"value": yv} for yv in y_vals]}
            ],
            "independent_variables": [
                {"header": {"name": "m_stau [GeV]", "units": "GeV"},
                 "values": [{"value": xv} for xv in x_vals]}
            ],            
        }
        tables.append(table)

    outname = f"{c}mm_hepdata_limits.yaml"
    # with open(outname, "w") as f_out:
    #     for table in tables:
    #         yaml.dump(table, f_out, sort_keys=False)
    #         f_out.write("\n---\n")  # separate multiple tables if needed


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


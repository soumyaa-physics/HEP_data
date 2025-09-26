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
        ey_low, ey_high = [], []

        for i in range(n):
            x = ctypes.c_double()
            y = ctypes.c_double()
            graph.GetPoint(i, x, y)
            x_vals.append(x.value)
            y_vals.append(y.value)

        if graph.InheritsFrom("TGraphAsymmErrors"):
            ey_low = [graph.GetEYlow()[i] for i in range(n)]
            ey_high = [graph.GetEYhigh()[i] for i in range(n)]
        else:
            # for plain TGraph, no errors
            ey_low = [0]*n
            ey_high = [0]*n

        table = {
            "name": label,
            "independent_variables": [
                {"header": {"name": "m_stau [GeV]", "units": "GeV"},
                 "values": [{"value": xv} for xv in x_vals]}
            ],
            "dependent_variables": [
                {"header": {"name": "95% CL limit", "units": "fb"},
                 "values": [{"value": yv,
                             "errors": [
                                 {"symerror": el, "label": "low"},
                                 {"symerror": eh, "label": "high"}
                             ]} for yv, el, eh in zip(y_vals, ey_low, ey_high)]}
            ]
        }
        tables.append(table)

    outname = f"{c}mm_hepdata_limits.yaml"
    with open(outname, "w") as f_out:
        yaml.dump({"tables": tables}, f_out, sort_keys=False)

    print(f"Output written to {outname}")
# notes: name of the tCanvas is
# limits-vs-mstau_10mm (TCanvas)
# which is made of TFrame TFrame
# and contains the following objects:
#hframe TH1F
# TLatex
#  TLatex
#  TLatex
# hframe_copy TH1F
# hframe_copy TH1F
# hframe_copy TH1F
# TFrame TFrame
# g1_xsecul_exp_pm2_10mm TGraphAsymmErrors
# g1_xsecul_exp_pm1_10mm TGraphAsymmErrors
# g1_xsecul_exp_10mm TGraph
# g1_xsecul_obs_10mm TGraph
# g1_xsec_theory_10mm TGraphAsymmErrors
# TPave TLegend
#  TLatex



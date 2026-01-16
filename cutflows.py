import yaml

input_file = "NEW_EXO-24-020_HEPData/data/cutflows_llstau_maximally-mixed_BR_2016_postVFP.2016_preVFP.2017.2018.yaml"
with open(input_file) as f:
    data = yaml.safe_load(f)

sample_key = list(data.keys())[0]
sample = data[sample_key]

sample_label = sample["label"]
cuts = sample["cuts"]

independent_var = {
    "header": {"name": "Selection step"},
    "values": [{"value": c["cut_label"]} for c in cuts]
}

dependent_vars = []
for sample_key, sample in data.items():

    sample_label = sample["label"]
    cuts = sample["cuts"]

    yield_var = {
        "header": {"name": "Event yield"},
        "qualifiers": [
            {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
            {"name": "SAMPLE", "value": sample_label},
            {"name": "LUMI", "value": "138 fb^{-1}"}
        ],
        "values": []
    }

    eff_var = {
        "header": {"name": "Selection efficiency"},
        "qualifiers": [
            {"name": "MODEL", "value": "GMSB maximally mixed stau scenario"},
            {"name": "SAMPLE", "value": sample_label}
        ],
        "values": []
    }

    for c in cuts:

        # ---- Yield entry ----
        y_entry = {"value": float(c["yield"])}

        if float(c["yield_unc_stat"]) > 0:
            y_entry["errors"] = [{
                "label": "stat",
                "symerror": float(c["yield_unc_stat"])
            }]

        yield_var["values"].append(y_entry)

        # Efficiency
        e_entry = {"value": float(c["efficiency"])}

        if float(c["efficiency_unc_stat"]) > 0:
            e_entry["errors"] = [{
                "label": "stat",
                "symerror": float(c["efficiency_unc_stat"])
            }]

        eff_var["values"].append(e_entry)

    dependent_vars.append(yield_var)
    dependent_vars.append(eff_var)

table = {
    "name": "Signal cutflows",
    "description": (
        "Signal yields and efficiencies in the maximally mixed scenario "
        "for the BR selections, for representative "
        "$(m_{\\tilde{\\tau}}, c\\tau_{0})$ values."
    ),
    "keywords": [
        {"name": "cmenergies", "values": [13000.0]}
    ],
    "dependent_variables": dependent_vars,
    "independent_variables": [independent_var]
}


outname = "cutflows.yaml"

with open(outname, "w") as f_out:

    yaml.dump({
        "dependent_variables": table["dependent_variables"],
        "independent_variables": table["independent_variables"],
        # "description": table["description"],
        # "keywords": table["keywords"],
        # "name": table["name"]
    }, f_out, sort_keys=False)

print("Output written to", outname)
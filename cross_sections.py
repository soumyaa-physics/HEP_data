import yaml

inputs = [
    {
        "file": "NEW_EXO-24-020_HEPData/data/crosssections_stau_mass-degenerate_hepi-fast.csv",
        "model": "Mass degenerate stau scenario",
        "tag": "Mass Degenerate"
    },
    {
        "file": "NEW_EXO-24-020_HEPData/data/crosssections_stau_maximally-mixed_hepi-fast.csv",
        "model": "Maximally mixed stau scenario",
        "tag": "Maximally Mixed"

    }
]

outname = "hepdata_cross-sections_stau-pair.yaml"

tables = []

for entry in inputs:

    infile = entry["file"]
    model_name = entry["model"]
    tag = entry["tag"]

    masses = []
    values = []
    err_tot = []
    err_pdf = []
    err_scale = []


    with open(infile) as f:

        for line in f:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = [p.strip() for p in line.split(",")]

            mass = float(parts[0])
            central = float(parts[1])

            tot_down = abs(float(parts[2]))
            tot_up = abs(float(parts[3]))

            pdf_down = abs(float(parts[4]))
            pdf_up = abs(float(parts[5]))

            scale_down = abs(float(parts[6]))
            scale_up = abs(float(parts[7]))

            masses.append(mass)
            values.append(central)

            err_tot.append((tot_down, tot_up))
            err_pdf.append((pdf_down, pdf_up))
            err_scale.append((scale_down, scale_up))

    independent_var = {
        "header": {"name": "m_stau", "units": "GeV"},
        "values": [{"value": m} for m in masses]
    }

    dependent_var = {
        "header": {
            "name": f"Theoretical cross sections for stau pair production ({tag})",
            "units": "fb"
        },
        "qualifiers": [
            {"name": "PROCESS", "value": "pp → stau stau"},
            {"name": "MODEL", "value": model_name},
            {"name": "SQRT(S)", "value": "13 TeV"}
        ],
        "values": []
    }

    for i in range(len(masses)):

        row = {
            "value": values[i],
            "errors": []
        }

        # Total uncertainty
        if err_tot[i][0] > 0 or err_tot[i][1] > 0:
            row["errors"].append({
                "label": "total",
                "asymerror": {
                    "minus": err_tot[i][0],
                    "plus": err_tot[i][1]
                }
            })

        # PDF uncertainty
        if err_pdf[i][0] > 0 or err_pdf[i][1] > 0:
            row["errors"].append({
                "label": "pdf",
                "asymerror": {
                    "minus": err_pdf[i][0],
                    "plus": err_pdf[i][1]
                }
            })

        # Scale uncertainty
        if err_scale[i][0] > 0 or err_scale[i][1] > 0:
            row["errors"].append({
                "label": "scale",
                "asymerror": {
                    "minus": err_scale[i][0],
                    "plus": err_scale[i][1]
                }
            })

        dependent_var["values"].append(row)

    table = {
        "name": "Theoretical cross sections for stau pair production",
        "description": (
            f"Theoretical cross sections at NLO+NLL accuracy for stau pair production in the {model_name}."
        ),
        "keywords": [
            {"name": "cmenergies", "values": [13000.0]},
            {"name": "observables", "values": ["cross section"]}
        ],
        "dependent_variables": [dependent_var],
        "independent_variables": [independent_var]
    }

    tables.append(table)


with open(outname, "w") as f_out:

    for table in tables:

        table_to_dump = {
            "dependent_variables": table["dependent_variables"],
            "independent_variables": table["independent_variables"],
            "description": table["description"],
            "keywords": table["keywords"],
            "name": table["name"]
        }

        yaml.dump(table_to_dump, f_out, sort_keys=False)
        f_out.write("\n")   # separate tables

print("Output written to", outname)
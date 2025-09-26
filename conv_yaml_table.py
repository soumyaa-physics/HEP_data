import yaml
import argparse
import os

parser = argparse.ArgumentParser(description="Convert nested raw YAML to HEPData YAML tables, one per method")
parser.add_argument("input_file", help="Path to the raw YAML file")
parser.add_argument("-o", "--output_dir", default=".", help="Directory to save HEPData YAML files")
args = parser.parse_args()

input_path = args.input_file
output_dir = args.output_dir

with open(input_path) as f:
    raw = yaml.safe_load(f)

era = list(raw.keys())[0]              # e.g., "2016_"
regions = list(raw[era]["misid"].keys())

# Gather all bins across all regions, sort numerically
all_bins = set()
for region in regions:
    all_bins.update(raw[era]["misid"][region].keys())
bins_sorted = sorted(all_bins, key=lambda x: int(x))

# Build markdown table
header = "| Bin | " + " | ".join(regions) + " |\n"
sep = "|---|" + "|".join("---" for _ in regions) + "|\n"
rows = []

for b in bins_sorted:
    row = f"| {b} "
    for region in regions:
        region_data = raw[era]["misid"][region]
        if b in region_data:
            y = region_data[b].get("yield")
            u = region_data[b].get("unc_abs")
            if y is not None and u is not None:
                cell = f"\( {y:.3g} \\pm {u:.3g} \)"
            else:
                cell = ""
        else:
            cell = ""
        row += f"| {cell} "
    row += "|\n"
    rows.append(row)

print(header + sep + "".join(rows))

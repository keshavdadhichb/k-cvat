import json
import os
import pandas as pd

# Automatically find the JSON file in the current directory
json_file = next((f for f in os.listdir() if f.endswith('.json')), None)
if not json_file:
    raise FileNotFoundError("No JSON file found in the current directory.")

# Load the JSON data
with open(json_file, 'r') as f:
    data = json.load(f)

# Extract label_id to label_name mapping
label_map = {i: label['name'] for i, label in enumerate(data['categories']['label']['labels'])}

# Extract all used label_ids in annotations
used_labels_set = set()
for item in data['items']:
    for ann in item.get('annotations', []):
        if 'label_id' in ann:
            used_labels_set.add(ann['label_id'])

# Only include labels that are actually used
used_labels = sorted(list(used_labels_set))
label_names = [label_map[i] for i in used_labels]

# Build data rows
rows = []
for item in data['items']:
    image_name = item['id']
    frame_number = item.get('attr', {}).get('frame', '')
    annotations = item.get('annotations', [])

    # Count annotations per used label
    label_counts = {label_map[i]: 0 for i in used_labels}
    for ann in annotations:
        label_id = ann.get('label_id')
        if label_id in label_counts:
            label_counts[label_map[label_id]] += 1

    row = {
        "Image Name": image_name,
        "Frame Number": frame_number,
        "Total Annotations": len(annotations),
        **label_counts
    }
    rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(rows)

# Sort columns: first three fixed, then label columns alphabetically
fixed_cols = ["Image Name", "Frame Number", "Total Annotations"]
label_cols = sorted([col for col in df.columns if col not in fixed_cols])
df = df[fixed_cols + label_cols]

# Export to CSV
output_file = "datumaro_annotation_summary.csv"
df.to_csv(output_file, index=False)

print(f"Done! CSV file saved as '{output_file}' with shape {df.shape}")

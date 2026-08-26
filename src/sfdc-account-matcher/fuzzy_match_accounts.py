import pandas as pd
from rapidfuzz import process, fuzz

# Load input files
global_df = pd.read_csv("global_2000.csv")
sfdc_df = pd.read_csv("sfdc_accounts.csv", encoding="latin1")

# Extract name columns
input_names = global_df['Name'].dropna().unique().tolist()
sfdc_names = sfdc_df['Account Name'].dropna().unique().tolist()

# Clean function
def normalize(name):
    if not isinstance(name, str):
        return ""
    return name.lower().replace(',', '').replace('.', '').replace('inc', '').replace('llc', '').strip()

# Build name list for matching
cleaned_sfdc = [normalize(name) for name in sfdc_names]

# Match each input
results = []
for original in input_names:
    query = normalize(original)
    matches = process.extract(query, cleaned_sfdc, scorer=fuzz.token_sort_ratio, limit=3)
    result = {
        "Input Name": original,
    }
    for i, (match_name, score, idx) in enumerate(matches):
        result[f"Match {i+1}"] = sfdc_names[idx]
        result[f"Score {i+1}"] = round(score, 1)
    results.append(result)

# Save to CSV
output_df = pd.DataFrame(results)
output_df.to_csv("fuzzy_matches_output.csv", index=False)
print("✅ Fuzzy matches saved to fuzzy_matches_output.csv")

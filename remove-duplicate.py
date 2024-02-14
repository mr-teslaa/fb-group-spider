import pandas as pd

# Read the Excel file
df = pd.read_excel("buy-and-sell_facebook_groups_dataset.xlsx")

# Drop duplicate rows based on "Group URL" column
df_unique = df.drop_duplicates(subset=["Group URL"])

# Save the updated DataFrame back to an Excel file
df_unique.to_excel("buy-and-sell_facebook_groups_dataset_cleaned.xlsx", index=False)

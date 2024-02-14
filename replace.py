import pandas as pd

# Read the Excel file
df = pd.read_excel("buy-and-sell_facebook_groups_dataset.xlsx")

# Replace '0' in "Today's Post" column with "No New Post Today"
df["Today's Post"] = df["Today's Post"].apply(lambda x: "No New Post Today" if x == 0 else x)

# Save the updated DataFrame back to an Excel file
df.to_excel("buy-and-sell_facebook_groups_dataset.xlsx", index=False)

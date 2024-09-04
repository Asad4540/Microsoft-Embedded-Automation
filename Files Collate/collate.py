import os
import pandas as pd

# Specify the directory containing the Excel files
folder_path = os.getcwd()

# List to hold dataframes
df_list = []

# Loop through each file in the directory
for file in os.listdir(folder_path):
    if file.endswith(".xlsx"):
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path)
        df_list.append(df)

# Concatenate all dataframes
collated_df = pd.concat(df_list, ignore_index=True)

# Write the collated dataframe to a new Excel file
collated_df.to_excel("collated_data.xlsx", index=False)

print("Collated data has been saved to 'collated_data.xlsx'")

import os
import pandas as pd

# Specify the directory containing the Excel files
folder_path = os.getcwd()
print(f"Folder path: {folder_path}\n")

# List to hold dataframes
df_list = []

# Loop through each file in the directory
for file in os.listdir(folder_path):
    if file.endswith(".xlsx"):
        file_path = os.path.join(folder_path, file)
        print(f"Processing file: {file_path}")
        
        # Read the Excel file
        df = pd.read_excel(file_path)
        # print(f"Columns in file: {df.columns.tolist()}")
        
        # Check if required columns are present in the dataframe
        required_columns = [
            "Asset Title / Ad Name", 
            "Vereigen Links", 
            "Snippets 8/27", 
            "Ungated PDFs of the localized eBooks/reports (include local links for all markets)"
        ]
        
        if all(column in df.columns for column in required_columns):
            # Filter out only the required columns
            df_filtered = df[required_columns]
            df_list.append(df_filtered)
            print(f"Successfully processed: {file_path}\n")  # Added a space after processing each file
        else:
            print(f"Skipping file {file_path} as it doesn't have the required columns.\n")

# Check if any dataframes were added
if df_list:
    # Concatenate all dataframes
    collated_df = pd.concat(df_list, ignore_index=True)
    
    # Write the collated dataframe to a new Excel file
    collated_df.to_excel("collated_data.xlsx", index=False)
    
    print("Collated data has been saved to 'collated_data.xlsx'")
else:
    print("No files were processed. Check if the files exist and contain the required columns.")

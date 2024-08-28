import pandas as pd
import re

# Load the Excel file
file_path = 'MD2808.xlsx'
df = pd.read_excel(file_path)

# Define a function to extract the value inside key=""
def extract_key_value(form_snippet):
    # Use regex to find the value inside key=""
    match = re.search(r'key="([^"]*)"', form_snippet)
    if match:
        return match.group(1)  # Return the value inside the quotes
    return None  # Return None if no match is found

# Apply the function to the "Form Snippet" column and create a new column with the results
df['Key Value'] = df['Form Snippet'].apply(extract_key_value)

# Save the updated DataFrame back to the same Excel file
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
    df.to_excel(writer, index=False)

print("Key values extracted and saved to the same Excel file.")

import os
import requests
from bs4 import BeautifulSoup
import openpyxl

# Load Excel file with URLs and script snippets
excel_file = 'scripts_to_replace.xlsx'
wb = openpyxl.load_workbook(excel_file)
sheet = wb.active

# Create 'local' directory if it doesn't exist
output_dir = 'local'
os.makedirs(output_dir, exist_ok=True)

# Iterate through each row in the Excel file
for row in sheet.iter_rows(min_row=2, values_only=True):
    # Only take the first two columns (URL and new script snippet)
    url, new_script = row[0], row[1]
    
    # Skip rows with missing or invalid URLs
    if not url or not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        print(f"Skipping invalid URL: {url}")
        continue
    
    # Fetch the HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the form tag and its script tag
    form_tag = soup.find('form')
    if form_tag:
        script_tag = form_tag.find('script')
        if script_tag:
            # Replace the script tag content
            script_tag.string = new_script
            
    # Save the modified HTML to a local file
    filename = url.split('/')[-1]  # Extract filename from URL
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

print("Scraping and replacement completed.")

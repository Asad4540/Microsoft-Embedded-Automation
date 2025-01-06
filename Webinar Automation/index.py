import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

def create_folder_structure(base_url):
    """Create folder structure from the base URL."""
    # Parse the base URL into folder components
    url_parts = base_url.split('/')
    folder_name = url_parts[3]  # First part of the path
    subfolders = url_parts[4:]  # Remaining parts of the path

    # Create the main folder and subfolders
    folder_path = os.path.join(folder_name, *subfolders)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return folder_path

def modify_html(soup, new_link):
    """Modify the HTML content by changing the div tag and form input link."""
    # Find the div with the data-iswebinar attribute and change its value
    div_tag = soup.find('div', {'data-iswebinar': 'false'})
    if div_tag:
        div_tag['data-iswebinar'] = 'true'
    
    # Find the form input tag with value="pdf/1.pdf" and replace it with the new link
    input_tag = soup.find('input', {'value': 'pdf/1.pdf'})
    if input_tag:
        input_tag['value'] = new_link

def scrape_and_modify(url, new_link):
    """Scrape the webpage and modify the HTML."""
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Modify the HTML
        modify_html(soup, new_link)
        
        return str(soup)
    else:
        print(f"Failed to retrieve {url}")
        return None

def main():
    # Load the Excel file
    excel_file = 'web_links.xlsx'
    df = pd.read_excel(excel_file)

    # Check if the required columns exist in the Excel file
    if 'updatedlink' not in df.columns or 'link' not in df.columns:
        print("Error: Required columns 'updatedlink' and 'link' not found in the Excel file.")
        return

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        # Ensure both 'updatedlink' and 'link' exist for the current row
        if pd.notna(row['updatedlink']) and pd.notna(row['link']):
            updatedlink = row['updatedlink']
            new_link = row['link']
            
            # Create folder structure based on the updatedlink
            folder_path = create_folder_structure(updatedlink)
            
            # Scrape the webpage and modify it
            modified_html = scrape_and_modify(updatedlink, new_link)
            
            if modified_html:
                # Determine the HTML file name
                html_filename = os.path.join(folder_path, 'index.html')
                
                # Save the modified HTML to the folder
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(modified_html)
                print(f"Modified HTML saved at {html_filename}")
            else:
                print(f"Skipping {updatedlink} due to error")
        else:
            print(f"Skipping row {index}: missing 'updatedlink' or 'link' value")

if __name__ == "__main__":
    main()

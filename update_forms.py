import pandas as pd
import requests
from bs4 import BeautifulSoup

def read_excel(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    # Print column names for debugging
    print("Columns in the Excel file:", df.columns.tolist())
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df

def fetch_webpage(url):
    # Fetch the HTML content of the webpage
    response = requests.get(url)
    return response.content

def replace_form_content(html_content, new_form_snippet):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Locate the <form> tag
    form_tag = soup.find('form')
    
    if form_tag:
        # Clear all content inside the form tag
        form_tag.clear()
        # Insert the new form snippet
        form_tag.append(BeautifulSoup(new_form_snippet, 'html.parser'))
        
        # Get the modified HTML
        return str(soup)
    else:
        return None

def save_modified_html(file_name, modified_html):
    # Save the modified HTML to a file
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(modified_html)

def process_excel(file_path):
    df = read_excel(file_path)
    
    for index, row in df.iterrows():
        url = row['URL']
        new_form_snippet = row['Form Snippet']
        
        # Fetch the webpage content
        html_content = fetch_webpage(url)
        
        # Replace the content inside the form tag in the HTML content
        modified_html = replace_form_content(html_content, new_form_snippet)
        
        if modified_html:
            # Save the modified HTML to a file
            save_modified_html(f'modified_{index}.html', modified_html)
            print(f'Successfully modified and saved HTML for {url}')
        else:
            print(f'No form tag found in {url}')

if __name__ == '__main__':
    excel_file_path = 'webpages_and_snippets.xlsx'
    process_excel(excel_file_path)

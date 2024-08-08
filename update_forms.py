import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def read_excel(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df

def fetch_webpage(url):
    # Fetch the HTML content of the webpage
    response = requests.get(url)
    return response.content

def download_image(image_url, output_folder):
    # Download the image and save it to the output folder
    response = requests.get(image_url)
    image_name = os.path.basename(urlparse(image_url).path)
    image_path = os.path.join(output_folder, image_name)

    with open(image_path, 'wb') as file:
        file.write(response.content)

    return image_name

def replace_image_paths(soup, output_folder, base_url):
    # Find all image tags
    for img_tag in soup.find_all('img'):
        img_url = img_tag['src']
        # Create the full URL if necessary
        full_img_url = urljoin(base_url, img_url)

        # Download the image and save it in the output folder
        image_name = download_image(full_img_url, output_folder)
        
        # Update the src attribute to the local path
        img_tag['src'] = os.path.join('images', image_name)

def replace_form_content(html_content, new_form_snippet, redirect_url, output_folder, base_url):
    # Replace the placeholder comment with the window.location.replace() code
    modified_snippet = new_form_snippet.replace('// Add code to deliver asset here', f'window.location.replace("{redirect_url}");')
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Replace image paths with local paths
    replace_image_paths(soup, output_folder, base_url)
    
    # Locate the <form> tag
    form_tag = soup.find('form')
    
    if form_tag:
        # Clear all content inside the form tag
        form_tag.clear()
        # Insert the modified form snippet
        form_tag.append(BeautifulSoup(modified_snippet, 'html.parser'))
        
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
    
    # Ensure the images folder exists
    images_folder = 'images'
    os.makedirs(images_folder, exist_ok=True)
    
    for index, row in df.iterrows():
        url = row['URL']
        new_form_snippet = row['Form Snippet']
        redirect_url = row['Redirect URL']  # Assuming there's a 'Redirect URL' column in the Excel
        
        # Fetch the webpage content
        html_content = fetch_webpage(url)
        
        # Replace the content inside the form tag in the HTML content
        modified_html = replace_form_content(html_content, new_form_snippet, redirect_url, images_folder, url)
        
        if modified_html:
            # Save the modified HTML to a file
            save_modified_html(f'modified_{index}.html', modified_html)
            print(f'Successfully modified and saved HTML for {url}')
        else:
            print(f'No form tag found in {url}')

if __name__ == '__main__':
    excel_file_path = 'webpages_and_snippets.xlsx'
    process_excel(excel_file_path)

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def read_excel(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Strip any extra spaces from column names
    return df

def fetch_webpage(url):
    response = requests.get(url)
    return response.content

def download_image(image_url, output_folder):
    response = requests.get(image_url)
    image_name = os.path.basename(urlparse(image_url).path)
    image_path = os.path.join(output_folder, image_name)

    with open(image_path, 'wb') as file:
        file.write(response.content)

    return image_name

def replace_image_paths(soup, output_folder, base_url):
    for img_tag in soup.find_all('img'):
        img_url = img_tag['src']
        full_img_url = urljoin(base_url, img_url)
        image_name = download_image(full_img_url, output_folder)
        img_tag['src'] = os.path.join('images', image_name)

def replace_form_content(html_content, new_form_snippet, redirect_url, output_folder, base_url):
    modified_snippet = new_form_snippet.replace('// Add code to deliver asset here', f'window.location.replace("https://{redirect_url}");')
    soup = BeautifulSoup(html_content, 'html.parser')
    replace_image_paths(soup, output_folder, base_url)
    form_tag = soup.find('form')

    if form_tag:
        form_tag.clear()
        form_tag.append(BeautifulSoup(modified_snippet, 'html.parser'))
        return str(soup)
    else:
        return None

def generate_filename_from_url(url, existing_filenames):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) >= 3:
        last_three = path_parts[-3:]
    else:
        last_three = path_parts
    
    base_filename = "-".join(last_three)
    filename = f"{base_filename}"
    
    counter = 1
    while filename in existing_filenames:
        filename = f"{base_filename}-{counter}"
        counter += 1
    
    existing_filenames.add(filename)
    return filename

def save_modified_html(file_name, modified_html):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(modified_html)

def process_excel(file_path):
    df = read_excel(file_path)
    images_folder = 'images'
    os.makedirs(images_folder, exist_ok=True)
    
    existing_filenames = set()

    for index, row in df.iterrows():
        url = row['URL']
        new_form_snippet = row['Form Snippet']
        redirect_url = row['Redirect URL']
        
        html_content = fetch_webpage(url)
        modified_html = replace_form_content(html_content, new_form_snippet, redirect_url, images_folder, url)
        
        if modified_html:
            file_name = generate_filename_from_url(url, existing_filenames)
            save_modified_html(file_name, modified_html)
            print(f'Successfully modified and saved HTML for {url} as {file_name}')
        else:
            print(f'No form tag found in {url}')

if __name__ == '__main__':
    excel_file_path = 'webpages_and_snippets.xlsx'
    process_excel(excel_file_path)

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# Function to sanitize filenames by removing invalid characters
def sanitize_filename(filename):
    # Remove characters that are invalid in Windows file names, such as \ / : * ? " < > |
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Function to read the Excel file and clean up column names
def read_excel(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Strip any extra spaces from column names
    return df

# Function to fetch the HTML content of a webpage
def fetch_webpage(url):
    response = requests.get(url)
    return response.content

# Function to download an image from a URL and save it in the specified folder
def download_image(image_url, output_folder):
    response = requests.get(image_url)
    image_name = os.path.basename(urlparse(image_url).path)
    image_name = sanitize_filename(image_name)  # Sanitize the filename
    image_path = os.path.join(output_folder, image_name)

    with open(image_path, 'wb') as file:
        file.write(response.content)

    return image_name

# Function to replace the image paths in the HTML content and download the images locally
def replace_image_paths(soup, output_folder, base_url):
    for img_tag in soup.find_all('img'):  # Loop through all <img> tags
        img_url = img_tag['src']  # Get the image URL from the src attribute
        full_img_url = urljoin(base_url, img_url)  # Build the full URL
        image_name = download_image(full_img_url, output_folder)  # Download the image
        img_tag['src'] = os.path.join('images', image_name)  # Update the src attribute to point to the local image

# Function to replace the content inside the <form> tag with a new form snippet
def replace_form_content(html_content, new_form_snippet, redirect_url, output_folder, base_url):
    # Replace the placeholder comment with the redirect URL in the new form snippet
    modified_snippet = new_form_snippet.replace('// Add code to deliver asset here', f'window.location.replace("https://{redirect_url}");')
    soup = BeautifulSoup(html_content, 'html.parser')  # Parse the HTML content
    
    # Remove the element with id="form-subheading"
    form_subheading_tag = soup.find(id="form-subheading")
    if form_subheading_tag:
        form_subheading_tag.decompose()  # Remove the tag entirely from the HTML
    
    replace_image_paths(soup, output_folder, base_url)  # Replace image paths and download images
    form_tag = soup.find('form')  # Find the <form> tag

    if form_tag:
        form_tag.clear()  # Remove all content inside the <form> tag
        form_tag.append(BeautifulSoup(modified_snippet, 'html.parser'))  # Add the new form snippet inside the <form> tag
        return str(soup)  # Return the modified HTML as a string
    else:
        return None

# Function to generate a folder name from the URL based on the first part after the domain
def generate_folder_name_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if path_parts:
        return path_parts[0]  # Return the first part after the domain as the folder name
    else:
        return 'default_folder'  # Fallback if no valid folder name can be extracted

# Function to generate a filename based on the last three parts of the URL path
def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) >= 3:
        last_three = path_parts[-3:]  # Get the last three parts of the URL path
    else:
        last_three = path_parts
    
    filename = "-".join(last_three)  # Join the parts with "-" to form the filename
    return filename

# Function to save the modified HTML content to a file in the specified folder
def save_modified_html(folder_name, file_name, modified_html):
    os.makedirs(folder_name, exist_ok=True)  # Create the folder if it doesn't exist
    file_path = os.path.join(folder_name, file_name)  # Construct the file path
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_html)

# Main function to process the Excel file and apply the modifications to each webpage
def process_excel(file_path):
    df = read_excel(file_path)  # Read the Excel file

    for index, row in df.iterrows():  # Loop through each row in the Excel file
        url = row['URL']  # Get the URL from the row
        new_form_snippet = row['Form Snippet']  # Get the new form snippet from the row
        redirect_url = row['Redirect URL']  # Get the redirect URL from the row
        
        html_content = fetch_webpage(url)  # Fetch the HTML content of the webpage
        
        # Determine the folder name from the URL
        folder_name = generate_folder_name_from_url(url)
        images_folder = os.path.join(folder_name, 'images')  # Images folder inside the new folder
        os.makedirs(images_folder, exist_ok=True)  # Create the images folder if it doesn't exist
        
        modified_html = replace_form_content(html_content, new_form_snippet, redirect_url, images_folder, url)  # Replace the form content and update the HTML
        
        if modified_html:
            file_name = generate_filename_from_url(url)  # Generate the filename for the modified HTML
            save_modified_html(folder_name, file_name, modified_html)  # Save the modified HTML to a file inside the new folder
            print(f'Successfully modified and saved HTML for {url} as {file_name} in folder {folder_name}')
        else:
            print(f'No form tag found in {url}')

if __name__ == '__main__':
    excel_file_path = 'scripts_to_replace.xlsx'  # Path to the Excel file containing URLs and snippets
    process_excel(excel_file_path)  # Process the Excel file

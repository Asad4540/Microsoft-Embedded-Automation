import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from flask import Flask, request, send_file, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import zipfile
import io

app = Flask(__name__)

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
    image_path = os.path.join(output_folder, image_name)

    with open(image_path, 'wb') as file:
        file.write(response.content)

    return image_name

# Function to replace the image paths in the HTML content and download the images locally
def replace_image_paths(soup, output_folder, base_url):
    for img_tag in soup.find_all('img'):
        img_url = img_tag['src']
        full_img_url = urljoin(base_url, img_url)
        image_name = download_image(full_img_url, output_folder)
        img_tag['src'] = os.path.join('images', image_name)

# Function to replace the content inside the <form> tag with a new form snippet
def replace_form_content(html_content, new_form_snippet, redirect_url, output_folder, base_url):
    modified_snippet = new_form_snippet.replace('// Add code to deliver asset here', f'window.location.replace("https://{redirect_url}");')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    form_subheading_tag = soup.find(id="form-subheading")
    if form_subheading_tag:
        form_subheading_tag.decompose()
    
    replace_image_paths(soup, output_folder, base_url)
    form_tag = soup.find('form')

    if form_tag:
        form_tag.clear()
        form_tag.append(BeautifulSoup(modified_snippet, 'html.parser'))
        return str(soup)
    else:
        return None

# Function to generate a folder name from the URL based on the first part after the domain
def generate_folder_name_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if path_parts:
        return path_parts[0]
    else:
        return 'default_folder'

# Function to generate a filename based on the last three parts of the URL path
def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) >= 3:
        last_three = path_parts[-3:]
    else:
        last_three = path_parts
    
    filename = "-".join(last_three)
    return filename

# Function to process the Excel file and create a zip of modified HTMLs
def process_excel(file_path):
    df = read_excel(file_path)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for index, row in df.iterrows():
            url = row['URL']
            new_form_snippet = row['Form Snippet']
            redirect_url = row['Redirect URL']
            html_content = fetch_webpage(url)
            
            folder_name = generate_folder_name_from_url(url)
            images_folder = os.path.join(folder_name, 'images')
            os.makedirs(images_folder, exist_ok=True)
            
            modified_html = replace_form_content(html_content, new_form_snippet, redirect_url, images_folder, url)
            
            if modified_html:
                file_name = generate_filename_from_url(url)
                html_path = os.path.join(folder_name, f'{file_name}.html')
                
                zip_file.writestr(html_path, modified_html)
            else:
                continue

    zip_buffer.seek(0)
    return zip_buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        # Ensure the 'uploads' directory exists
        os.makedirs('uploads', exist_ok=True)
        
        # Save the uploaded file in the 'uploads' directory
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        # Process the file and return the zip
        zip_buffer = process_excel(file_path)
        return send_file(zip_buffer, as_attachment=True, download_name='modified_htmls.zip', mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)

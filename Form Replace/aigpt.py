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

# Function to replace the content inside the <form> tag with a new form snippet
def replace_form_content(html_content, new_form_snippet, redirect_url, output_folder, base_url):
    modified_snippet = new_form_snippet.replace('// Add code to deliver asset here', f'window.location.replace("https://{redirect_url}");')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find and update all tags with data-isembedded="false"
    for tag in soup.find_all(attrs={"data-isembedded": "false"}):
        tag['data-isembedded'] = "true"  # Update the attribute to "true"
    
    # Remove the element with id="form-subheading"
    form_subheading_tag = soup.find(id="form-subheading")
    if form_subheading_tag:
        form_subheading_tag.decompose()
    
    # replace_image_paths(soup, output_folder, base_url)
    form_tag = soup.find('form')

    if form_tag:
        form_tag.clear()
        form_tag.append(BeautifulSoup(modified_snippet, 'html.parser'))
        return str(soup)
    else:
        return None

# Function to generate folder structure based on the URL path
def generate_folder_name_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) > 1:
        # Generate the folder structure up to the second last part (excluding the last part, which is the file)
        folder_structure = os.path.join(*path_parts[:-1])
        return folder_structure
    else:
        return 'default_folder'  # Fallback if no valid folder name can be extracted

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
            
            # Generate the folder structure based on the URL
            folder_structure = generate_folder_name_from_url(url)
            images_folder = os.path.join(folder_structure, 'images')  # Subfolder for images
            
            os.makedirs(images_folder, exist_ok=True)  # Create the entire folder structure
            
            # Modify the HTML content
            modified_html = replace_form_content(html_content, new_form_snippet, redirect_url, images_folder, url)
            
            if modified_html:
                file_name = generate_filename_from_url(url)
                html_path = os.path.join(folder_structure, f'{file_name}')
                
                zip_file.writestr(html_path, modified_html)  # Add to zip file
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

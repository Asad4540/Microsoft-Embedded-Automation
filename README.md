# Webpage HTML Modifier and Image Downloader

This Python script automates the modification of HTML content for multiple webpages by processing a list of URLs and corresponding form snippets from an Excel file. The script performs the following actions for each webpage:

1. **Fetch HTML Content**: Downloads the HTML content of the provided URL.
2. **Replace Form Content**: Identifies the `<form>` tag in the HTML and replaces its content with a new form snippet provided in the Excel file.
3. **Download Images Locally**: Downloads all images referenced in the HTML, saving them to a specified folder.
4. **Modify Image Paths**: Replaces the image URLs in the HTML content with local paths.
5. **Remove Specific HTML Elements**: Removes specific HTML elements, such as those with a certain ID (e.g., `form-subheading`), if present.
6. **Save Modified HTML**: Saves the modified HTML content to a new file in a structured folder system.

## Features

- **Excel Input**: Provides an easy way to manage multiple webpages and corresponding snippets using an Excel file.
- **Image Downloading**: Automatically fetches images from webpages and saves them locally, updating the HTML to reference these local images.
- **HTML Modification**: Customizes the HTML by replacing form tags and removing specified elements.
- **File Organization**: Organizes the modified HTML files and downloaded images into folders based on the URLs.

## Requirements

- Python 3.x
- Pandas
- Requests
- BeautifulSoup4 (bs4)
- Openpyxl (for reading Excel files)

Install the dependencies using:

```bash
pip install pandas requests beautifulsoup4 openpyxl
```

## Usage

1. Prepare an Excel file (`webpages_and_snippets.xlsx`) with the following columns:
   - **URL**: The URL of the webpage to fetch.
   - **Form Snippet**: The new HTML form snippet to replace the existing form content.
   - **Redirect URL**: The URL to which the user will be redirected after form submission.

2. Run the script:

```bash
python script_name.py
```

3. The script will process each row in the Excel file, download the HTML content of the webpage, modify the HTML, download the images, and save the modified HTML and images in structured folders.

4. After processing, the output will be saved in a folder structure based on the URLs, with modified HTML files and downloaded images.

## Example

Assuming the Excel file contains the following data:

| URL                   | Form Snippet                          | Redirect URL          |
|-----------------------|---------------------------------------|-----------------------|
| https://example.com/a  | `<form>New Form Content</form>`       | example.com/redirect  |
| https://example.com/b  | `<form>Another Form Snippet</form>`   | example.com/thankyou  |

The script will:

- Download the HTML content from `https://example.com/a` and `https://example.com/b`.
- Replace the existing form content with the corresponding form snippets.
- Download and save all images locally in folders `a/images` and `b/images`.
- Save the modified HTML files as `a.html` and `b.html`.

## Configuration

- **Folder and Filename Generation**: The script generates folder names from the first part of the URL path and filenames based on the last three parts of the URL path.
- **HTML Element Removal**: Elements with the ID `form-subheading` are removed from the HTML content, if present.

## Customization

You can customize the script further by modifying the `replace_form_content` function or adding additional functionality to suit your specific needs.

## License

This project is licensed under the MIT License. Feel free to use and modify the script for your own purposes.


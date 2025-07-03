import os
import requests
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import pypdf
import ollama

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_documents():
    if 'documents' not in request.files:
        return render_template('index.html', error='No file part')

    files = request.files.getlist('documents')
    target_language = request.form.get('target_language')

    if not files or files[0].filename == '':
        return render_template('index.html', error='No selected file')
    if not target_language:
        return render_template('index.html', error='Target language not specified')

    translated_texts = {}
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            extracted_text = ""
            if filename.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(filepath)
            else:
                # Assume it's docx or doc, convert to PDF
                try:
                    converted_pdf_path = convert_to_pdf_service(filepath)
                    if converted_pdf_path:
                        extracted_text = extract_text_from_pdf(converted_pdf_path)
                        os.remove(converted_pdf_path) # Clean up converted PDF
                    else:
                        translated_texts[filename] = f"Error: Could not convert {filename} to PDF."
                        continue
                except Exception as e:
                    translated_texts[filename] = f"Error converting {filename}: {str(e)}"
                    continue
            
            os.remove(filepath) # Clean up original uploaded file

            if extracted_text:
                try:
                    # Instruct the model to preserve formatting as much as possible
                    prompt = f"Translate the following text to {target_language}, preserving paragraph breaks and headings:{extracted_text}"
                    response = ollama.chat(model='aya23', messages=[{'role': 'user', 'content': prompt}])
                    translated_texts[filename] = response['message']['content']
                except Exception as e:
                    translated_texts[filename] = f"Error translating {filename}: {str(e)}"
            else:
                translated_texts[filename] = f"No text extracted from {filename}."
        else:
            translated_texts[file.filename] = "Invalid file type or no file selected."

    return render_template('index.html', translated_texts=translated_texts)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n" # Add newlines between pages
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""
    return text

def convert_to_pdf_service(filepath):
    # This function sends the document to your local conversion service
    # and expects a PDF file in return.
    converter_url = "http://localhost:1234/convert_to_pdf"
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'application/octet-stream')}
            response = requests.post(converter_url, files=files)
            response.raise_for_status() # Raise an exception for HTTP errors

            if response.headers['Content-Type'] == 'application/pdf':
                converted_filename = secure_filename(os.path.basename(filepath).rsplit('.', 1)[0] + '.pdf')
                converted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], converted_filename)
                with open(converted_filepath, 'wb') as out_f:
                    out_f.write(response.content)
                return converted_filepath
            else:
                print(f"Conversion service did not return a PDF for {filepath}. Content-Type: {response.headers['Content-Type']}")
                return None
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the conversion service at {converter_url}. Please ensure it is running.")
        return None
    except Exception as e:
        print(f"Error during conversion of {filepath}: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)

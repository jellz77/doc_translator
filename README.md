# Document Translator

A Flask web application for uploading and translating documents (PDF, DOCX, DOC) into your chosen language using Ollama and a local document conversion service.

## Features

- Upload multiple documents (PDF, DOCX, DOC)
- Automatic conversion of DOCX/DOC to PDF via a local service
- Extracts text from PDFs
- Translates extracted text to a target language using Ollama
- Clean, Bootstrap-powered UI

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/)
- A local document conversion service running at `http://localhost:1234/convert_to_pdf` (for DOCX/DOC to PDF)
- The following Python packages (see [`requirements.txt`](requirements.txt)):
  - Flask
  - python-dotenv
  - requests
  - pypdf
  - ollama

## Installation

1. Clone this repository.
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Ensure Ollama is running and the `aya23` model is available.
4. Start your local document conversion service at `http://localhost:1234/convert_to_pdf`.

## Usage

1. Run the Flask app:
    ```sh
    python app.py
    ```
2. Open your browser and go to [http://localhost:5000](http://localhost:5000).
3. Upload your documents, specify the target language, and click "Translate".

## File Structure

```
.
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── uploads/
└── .gitignore
```

- [`app.py`](app.py): Main Flask application.
- [`templates/index.html`](templates/index.html): HTML template for the web UI.
- `uploads/`: Temporary storage for uploaded and converted files.

## Notes

- The app deletes uploaded and converted files after processing.
- For DOCX/DOC files, you must have a compatible conversion service running locally.
- Translation is performed using the Ollama `aya23` model.

## License

MIT License

"""
Document parser for non-code files.
"""
import json
from pathlib import Path

def parse_documents_to_json(file_paths, output_path):
    """
    Parse non-code documents and save results to JSON.
    """
    results = []

    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        result = {
            "path": str(file_path),
            "name": file_path.name,
            "type": file_path.suffix.lower().lstrip('.'),
            "content": "",
            "success": False,
            "error": ""
        }

        try:
            if not file_path.exists():
                result["error"] = "File does not exist"
            elif file_path.suffix.lower() == '.pdf':
                result["content"] = _extract_pdf_text(file_path)
                result["success"] = True
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                result["content"] = _extract_word_text(file_path)
                result["success"] = True
            elif file_path.suffix.lower() in ['.txt', '.md', '.markdown']:
                result["content"] = _extract_text_file(file_path)
                result["success"] = True
            else:
                result["error"] = f"Unsupported file type: {file_path.suffix}"

        except Exception as e:
            result["error"] = str(e)

        results.append(result)

    # Save to JSON
    output_data = {"files": results}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

def _extract_pdf_text(file_path):
    """Extract text from PDF file."""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except ImportError:
        raise Exception("PyPDF2 not installed")
    except Exception as e:
        raise Exception(f"PDF extraction failed: {e}")

def _extract_word_text(file_path):
    """Extract text from Word document."""
    try:
        import docx
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        return text.strip()
    except ImportError:
        raise Exception("python-docx not installed")
    except Exception as e:
        raise Exception(f"Word extraction failed: {e}")

def _extract_text_file(file_path):
    """Extract text from plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    except Exception as e:
        raise Exception(f"Text extraction failed: {e}")
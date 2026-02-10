from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uuid, os
from pathlib import Path
import shutil

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/upload-file", response_class=HTMLResponse)
def upload_page():
    # Show a frontend page for uploading file
    return """
    <html>
        <body>
            <h2>Upload Your ZIP File</h2>
            <form action="/upload-file" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    """

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(None)):
    # Validate presence and extension
    if file is None or not file.filename or not file.filename.lower().endswith(".zip"):
        # Return an HTML page that alerts then redirects back to the upload form
        return HTMLResponse(
            """
            <script>
            alert('Please upload a ZIP file. Only .zip files are allowed.');
            window.location.href = '/upload-file';
            </script>
            """,
            status_code=400,
        )

    # get the upload id
    upload_id = str(uuid.uuid4())
    dest = Path(UPLOAD_DIR) / f"{upload_id}.zip"

    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"status": "ok", "upload_id": upload_id}

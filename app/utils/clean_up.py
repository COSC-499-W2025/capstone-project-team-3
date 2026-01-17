from pathlib import Path
from typing import Optional
import shutil
import os

DEFAULT_UPLOADS_DIR = os.getenv("UPLOAD_DIR", "app/uploads")

def cleanup_upload(upload_id: str, extracted_dir: Optional[str] = None, delete_extracted: bool = False) -> dict:
	"""Delete artifacts (project contents) after generating insights"""
	if not upload_id:
		return {"status": "error", "reason": "upload_id required"}

	uploads_dir = DEFAULT_UPLOADS_DIR
	zip_path = Path(uploads_dir) / f"{upload_id}.zip"
	extracted_deleted = False
	zip_deleted = False

	# Delete the uploaded ZIP if present
	try:
		if zip_path.exists():
			zip_path.unlink()
			zip_deleted = True
	except Exception as exc:
		return {"status": "error", "reason": f"failed to delete zip: {exc}"}

	# Optionally delete extracted directory supplied by caller
	if delete_extracted and extracted_dir:
		ed = Path(extracted_dir)
		try:
			if ed.exists() and ed.is_dir():
				shutil.rmtree(ed, ignore_errors=False)
				extracted_deleted = True
		except Exception as exc:
			return {"status": "error", "reason": f"failed to delete extracted dir: {exc}"}

	# Also attempt to delete any stray folder under uploads_dir matching the upload_id
	stray_dir = Path(uploads_dir) / upload_id
	if stray_dir.exists() and stray_dir.is_dir():
		try:
			shutil.rmtree(stray_dir, ignore_errors=True)
		except Exception:
			# Ignore failures here
			pass

	return {
		"status": "ok",
		"zip_deleted": zip_deleted,
		"extracted_deleted": extracted_deleted,
	}
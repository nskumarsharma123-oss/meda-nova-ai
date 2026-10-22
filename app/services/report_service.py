import uuid
import logging
from pathlib import Path
from typing import Dict, Any
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from config import Config

logger = logging.getLogger(__name__)


class ReportService:
    @staticmethod
    def process_and_save(file_storage: FileStorage, session_id: str, clinical_notes: str = "") -> Dict[str, Any]:
        """
        Validates, sanitizes, and securely stores an uploaded report.
        """
        if not file_storage or not file_storage.filename:
            raise ValueError("No file provided.")

        original_filename = secure_filename(file_storage.filename)
        if not original_filename:
            raise ValueError("Invalid filename.")

        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        if ext not in Config.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type '.{ext}' is not permitted. Permitted types: {', '.join(Config.ALLOWED_EXTENSIONS)}")

        # Check content length
        file_storage.seek(0, 2)
        file_size = file_storage.tell()
        file_storage.seek(0)

        if file_size > Config.MAX_CONTENT_LENGTH:
            raise ValueError(f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum limit of {Config.MAX_CONTENT_LENGTH / (1024*1024):.0f}MB.")

        if file_size == 0:
            raise ValueError("The uploaded file is empty.")

        # Secure random stored filename to avoid collision and traversal
        stored_filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = Path(Config.UPLOAD_FOLDER)
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest_path = upload_dir / stored_filename

        # Save to private upload folder
        file_storage.save(str(dest_path))

        # Safe preview extraction for text files only (up to 2000 chars)
        extracted_notes = ""
        if ext == "txt":
            try:
                dest_path_resolved = dest_path.resolve()
                if not str(dest_path_resolved).startswith(str(upload_dir.resolve())):
                    raise ValueError("Illegal path traversal detected.")
                with open(dest_path_resolved, "r", encoding="utf-8", errors="replace") as f:
                    extracted_notes = f.read(2000)
            except Exception as e:
                logger.warning(f"Could not read text preview: {e}")
        elif ext == "pdf":
            extracted_notes = "Binary PDF document stored securely. Text extraction can be processed in clinical pipelines."

        if clinical_notes:
            extracted_notes = f"Clinical Notes: {clinical_notes}\n\nDocument Preview:\n{extracted_notes}"

        return {
            "session_id": session_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_type": ext,
            "file_size": file_size,
            "extracted_notes": extracted_notes,
        }

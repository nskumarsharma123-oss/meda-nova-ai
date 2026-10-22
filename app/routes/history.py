from pathlib import Path
import uuid
from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import PatientCase, UploadedReport
from app.extensions import db
from config import Config

history_bp = Blueprint("history", __name__)


def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    return session["session_id"]


@history_bp.route("/")
def list_history():
    sid = ensure_session_id()
    cases = PatientCase.query.filter_by(session_id=sid).order_by(PatientCase.created_at.desc()).all()
    reports = UploadedReport.query.filter_by(session_id=sid).order_by(UploadedReport.uploaded_at.desc()).all()
    return render_template("history.html", cases=cases, reports=reports)


@history_bp.route("/clear", methods=["POST"])
def clear_history():
    sid = ensure_session_id()

    # Delete reports files
    reports = UploadedReport.query.filter_by(session_id=sid).all()
    for r in reports:
        p = Path(Config.UPLOAD_FOLDER) / r.stored_filename
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass

    UploadedReport.query.filter_by(session_id=sid).delete()
    PatientCase.query.filter_by(session_id=sid).delete()
    db.session.commit()

    flash("Session analysis history and uploaded documents have been cleared.", "info")
    return redirect(url_for("history.list_history"))

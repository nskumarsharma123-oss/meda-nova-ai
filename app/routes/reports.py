import os
import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort
from app.forms import ReportUploadForm
from app.models import UploadedReport
from app.extensions import db
from app.services.report_service import ReportService
from config import Config

reports_bp = Blueprint("reports", __name__)


def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    return session["session_id"]


@reports_bp.route("/", methods=["GET", "POST"])
def upload():
    sid = ensure_session_id()
    form = ReportUploadForm()

    if form.validate_on_submit():
        try:
            report_data = ReportService.process_and_save(
                file_storage=form.report_file.data,
                session_id=sid,
                clinical_notes=form.clinical_notes.data or "",
            )

            record = UploadedReport(
                session_id=sid,
                original_filename=report_data["original_filename"],
                stored_filename=report_data["stored_filename"],
                file_type=report_data["file_type"],
                file_size=report_data["file_size"],
                extracted_notes=report_data["extracted_notes"],
            )

            db.session.add(record)
            db.session.commit()
            flash("Clinical document uploaded and processed securely.", "success")
            return redirect(url_for("reports.upload"))

        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            db.session.rollback()
            flash("An unexpected error occurred while processing the upload.", "danger")

    reports = UploadedReport.query.filter_by(session_id=sid).order_by(UploadedReport.uploaded_at.desc()).all()
    return render_template("reports.html", form=form, reports=reports)


@reports_bp.route("/delete/<int:report_id>", methods=["POST"])
def delete_report(report_id):
    sid = ensure_session_id()
    report = UploadedReport.query.filter_by(id=report_id, session_id=sid).first()
    if not report:
        abort(404)

    # Remove file from disk
    file_path = Path(Config.UPLOAD_FOLDER) / report.stored_filename
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass

    db.session.delete(report)
    db.session.commit()
    flash("Report removed successfully.", "info")
    return redirect(url_for("reports.upload"))

import uuid
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort
from app.forms import PatientAnalysisForm
from app.models import PatientCase
from app.extensions import db
from app.services.gemini_service import GeminiService
from app.services.disease_service import DiseaseService

analysis_bp = Blueprint("analysis", __name__)


def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    return session["session_id"]


@analysis_bp.route("/", methods=["GET", "POST"])
def index():
    sid = ensure_session_id()
    form = PatientAnalysisForm()

    if form.validate_on_submit():
        case_data = {
            "age": form.age.data,
            "gender": form.gender.data,
            "duration": form.duration.data,
            "symptoms": form.symptoms.data,
            "medical_history": form.medical_history.data or "",
            "family_history": form.family_history.data or "",
            "lab_findings": form.lab_findings.data or "",
        }

        # 1. Run AI analysis service
        gemini_service = GeminiService()
        ai_result = gemini_service.analyze_case(case_data)

        # 2. Run heuristic knowledge-base match
        disease_service = DiseaseService()
        kb_matches = disease_service.find_matches(form.symptoms.data)

        # 3. Store record in database linked to current session
        case_record = PatientCase(
            session_id=sid,
            age=form.age.data,
            gender=form.gender.data,
            duration=form.duration.data,
            symptoms=form.symptoms.data,
            medical_history=form.medical_history.data,
            family_history=form.family_history.data,
            lab_findings=form.lab_findings.data,
            ai_summary=ai_result.get("summary", ""),
            possible_conditions=ai_result.get("possible_conditions", []),
            clinical_observations=ai_result.get("clinical_observations", ""),
            reasons_insufficient=ai_result.get("reasons_insufficient", ""),
            missing_information=ai_result.get("missing_information", ""),
            safety_notes=ai_result.get("safety_disclaimer", ""),
        )

        try:
            db.session.add(case_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Database save error occurred. Analysis displayed below.", "warning")

        return render_template(
            "results.html",
            case=case_record,
            ai_result=ai_result,
            kb_matches=kb_matches,
        )

    return render_template("analysis.html", form=form)


@analysis_bp.route("/case/<int:case_id>")
def view_case(case_id):
    sid = ensure_session_id()
    case = PatientCase.query.filter_by(id=case_id, session_id=sid).first()
    if not case:
        abort(404)

    disease_service = DiseaseService()
    kb_matches = disease_service.find_matches(case.symptoms)

    ai_result = {
        "success": True,
        "configured": True,
        "summary": case.ai_summary or "Historical summary",
        "clinical_observations": case.clinical_observations or "",
        "possible_conditions": case.possible_conditions or [],
        "reasons_insufficient": case.reasons_insufficient or "",
        "missing_information": case.missing_information or "",
        "safety_disclaimer": case.safety_notes or "",
    }

    return render_template("results.html", case=case, ai_result=ai_result, kb_matches=kb_matches)

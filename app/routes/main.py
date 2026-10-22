from flask import Blueprint, render_template, request, session, abort
import uuid
from app.services.disease_service import DiseaseService
from app.models import PatientCase, UploadedReport

main_bp = Blueprint("main", __name__)


def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    return session["session_id"]


@main_bp.route("/")
def index():
    ensure_session_id()
    disease_service = DiseaseService()
    diseases = disease_service.get_all_diseases()
    return render_template("index.html", disease_count=len(diseases))


@main_bp.route("/dashboard")
def dashboard():
    sid = ensure_session_id()
    recent_cases = PatientCase.query.filter_by(session_id=sid).order_by(PatientCase.created_at.desc()).limit(5).all()
    recent_reports = UploadedReport.query.filter_by(session_id=sid).order_by(UploadedReport.uploaded_at.desc()).limit(5).all()
    disease_service = DiseaseService()
    diseases = disease_service.get_all_diseases()
    return render_template(
        "dashboard.html",
        cases=recent_cases,
        reports=recent_reports,
        disease_count=len(diseases),
    )


@main_bp.route("/knowledge-base")
def knowledge_base():
    ensure_session_id()
    query = request.args.get("q", "").strip()
    disease_service = DiseaseService()
    all_diseases = disease_service.get_all_diseases()

    if query:
        q_lower = query.lower()
        filtered = [
            d for d in all_diseases
            if q_lower in d["name"].lower()
            or q_lower in d["category"].lower()
            or any(q_lower in s.lower() for s in d.get("typical_symptoms", []))
        ]
    else:
        filtered = all_diseases

    return render_template("knowledge_base.html", diseases=filtered, query=query)


@main_bp.route("/knowledge-base/<disease_id>")
def knowledge_base_detail(disease_id):
    ensure_session_id()
    disease_service = DiseaseService()
    disease = disease_service.get_disease_by_id(disease_id)
    if not disease:
        abort(404)
    return render_template("knowledge_base_detail.html", disease=disease)


@main_bp.route("/about")
def about():
    ensure_session_id()
    return render_template("about.html")

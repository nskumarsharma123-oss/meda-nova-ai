import sys
from pathlib import Path

# Ensure project root and venv site-packages are in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

venv_site_packages = project_root / "venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
    sys.path.insert(0, str(venv_site_packages))

import pytest
from app.models import PatientCase, UploadedReport
from app.extensions import db


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MedNova" in response.data
    assert b"Rare Diseases" in response.data


def test_dashboard_route(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Research Dashboard" in response.data


def test_knowledge_base_list(client):
    response = client.get("/knowledge-base")
    assert response.status_code == 200
    assert b"Ehlers-Danlos" in response.data
    assert b"Wilson Disease" in response.data


def test_knowledge_base_search(client):
    response = client.get("/knowledge-base?q=copper")
    assert response.status_code == 200
    assert b"Wilson Disease" in response.data


def test_knowledge_base_detail_valid(client):
    response = client.get("/knowledge-base/fabry-disease")
    assert response.status_code == 200
    assert b"Fabry Disease" in response.data
    assert b"Lysosomal Storage Disorder" in response.data


def test_knowledge_base_detail_invalid(client):
    response = client.get("/knowledge-base/unknown-disease-xyz")
    assert response.status_code == 404
    assert b"Clinical Record or Page Not Found" in response.data


def test_about_route(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About MedNova AI" in response.data
    assert b"Safety &amp; Ethics" in response.data or b"Safety & Ethics" in response.data


def test_analysis_get_route(client):
    response = client.get("/analysis/")
    assert response.status_code == 200
    assert b"Patient Symptom &amp; Clinical Intake" in response.data or b"Patient Symptom & Clinical Intake" in response.data
    assert b"Ethical Research Consent" in response.data


def test_analysis_post_valid_flow(client):
    response = client.post(
        "/analysis/",
        data={
            "age": 34,
            "gender": "female",
            "duration": "18 months",
            "symptoms": "Marked joint hypermobility, frequent subluxations, and chronic pain in extremities.",
            "medical_history": "History of recurrent sprains.",
            "family_history": "Mother had hypermobile joints.",
            "lab_findings": "Normal rheumatoid factor and ANA titers.",
            "consent": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Clinical Differential Findings" in response.data
    assert b"Ehlers-Danlos" in response.data
    assert b"CRITICAL MEDICAL DISCLAIMER" in response.data


def test_analysis_view_existing_case(client):
    client.post(
        "/analysis/",
        data={
            "age": 22,
            "gender": "male",
            "duration": "2 years",
            "symptoms": "Tremors, dystonia, and abnormal liver enzyme tests.",
            "consent": "y",
        },
    )
    case = PatientCase.query.first()
    assert case is not None

    response = client.get(f"/analysis/case/{case.id}")
    assert response.status_code == 200
    assert b"Clinical Differential Findings" in response.data


def test_report_upload_flow(client):
    import io
    data = {
        "report_file": (io.BytesIO(b"Synthetic lab panel: Normal metabolic profile."), "report.txt"),
        "clinical_notes": "Routine screening notes",
        "consent": "y",
    }
    response = client.post("/reports/", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Clinical document uploaded and processed securely" in response.data
    assert b"report.txt" in response.data


def test_history_list_empty(client):
    response = client.get("/history/")
    assert response.status_code == 200
    assert b"Session Analysis History" in response.data
    assert b"No patient cases analyzed yet" in response.data


def test_history_clear(client):
    # Add a mock case first
    with client.session_transaction() as sess:
        sess["session_id"] = "test-session-123"

    case = PatientCase(
        session_id="test-session-123",
        age=30,
        gender="female",
        duration="1 year",
        symptoms="Chronic fatigue and hypermobility",
    )
    db.session.add(case)
    db.session.commit()

    # Clear history
    response = client.post("/history/clear", follow_redirects=True)
    assert response.status_code == 200
    assert b"Session analysis history and uploaded documents have been cleared" in response.data

    # Verify case is deleted
    assert PatientCase.query.filter_by(session_id="test-session-123").count() == 0


def test_security_headers(client):
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


if __name__ == "__main__":
    pytest.main([__file__])


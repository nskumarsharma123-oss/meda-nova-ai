import io
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
from flask import Flask

# Ensure project root is in sys.path when executed directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.forms import PatientAnalysisForm, ReportUploadForm
from werkzeug.datastructures import FileStorage


def test_patient_form_valid(app: Flask):
    with app.test_request_context():
        form = PatientAnalysisForm(data={
            "age": 28,
            "gender": "female",
            "duration": "6 months",
            "symptoms": "Episodic joint laxity and unusual skin fragility with recurrent dislocations.",
            "consent": True,
        })
        assert form.validate() is True


def test_patient_form_invalid_age(app: Flask):
    with app.test_request_context():
        # Age > 120
        form = PatientAnalysisForm(data={
            "age": 145,
            "gender": "male",
            "duration": "1 year",
            "symptoms": "Chronic fatigue",
            "consent": True,
        })
        assert form.validate() is False
        assert "age" in form.errors

        # Negative age
        form_neg = PatientAnalysisForm(data={
            "age": -5,
            "gender": "male",
            "duration": "1 year",
            "symptoms": "Chronic fatigue",
            "consent": True,
        })
        assert form_neg.validate() is False
        assert "age" in form_neg.errors


def test_patient_form_missing_symptoms(app: Flask):
    with app.test_request_context():
        form = PatientAnalysisForm(data={
            "age": 30,
            "gender": "female",
            "duration": "2 weeks",
            "symptoms": "",
            "consent": True,
        })
        assert form.validate() is False
        assert "symptoms" in form.errors


def test_patient_form_symptoms_too_short(app: Flask):
    with app.test_request_context():
        form = PatientAnalysisForm(data={
            "age": 30,
            "gender": "female",
            "duration": "2 weeks",
            "symptoms": "pain",  # only 4 chars, min is 5
            "consent": True,
        })
        assert form.validate() is False
        assert "symptoms" in form.errors


def test_patient_form_excessive_length(app: Flask):
    with app.test_request_context():
        long_symptoms = "A" * 4500  # max is 4000
        form = PatientAnalysisForm(data={
            "age": 30,
            "gender": "female",
            "duration": "2 weeks",
            "symptoms": long_symptoms,
            "consent": True,
        })
        assert form.validate() is False
        assert "symptoms" in form.errors


def test_patient_form_missing_consent(app: Flask):
    with app.test_request_context():
        form = PatientAnalysisForm(data={
            "age": 30,
            "gender": "female",
            "duration": "2 weeks",
            "symptoms": "Persistent unexplained symptoms over years.",
            "consent": False,
        })
        assert form.validate() is False
        assert "consent" in form.errors


def test_report_upload_form_disallowed_extension(app: Flask):
    with app.test_request_context():
        fake_exe = FileStorage(
            stream=io.BytesIO(b"malicious executable payload"),
            filename="malicious.exe",
            content_type="application/x-msdownload",
        )
        form = ReportUploadForm(data={"report_file": fake_exe, "consent": True})
        assert form.validate() is False
        assert "report_file" in form.errors


if __name__ == "__main__":
    pytest.main([__file__])



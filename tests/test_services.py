import io
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root and venv site-packages are in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

venv_site_packages = project_root / "venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
    sys.path.insert(0, str(venv_site_packages))

from unittest.mock import MagicMock
import pytest
from flask import Flask

from werkzeug.datastructures import FileStorage
from app.services.disease_service import DiseaseService
from app.services.gemini_service import GeminiService
from app.services.report_service import ReportService


# ---------------------------------------------------------------------------
# DiseaseService Tests
# ---------------------------------------------------------------------------
def test_disease_service_load_and_lookup():
    service = DiseaseService()
    diseases = service.get_all_diseases()
    assert len(diseases) >= 5

    wilson = service.get_disease_by_id("wilson-disease")
    assert wilson is not None
    assert "Wilson Disease" in wilson["name"]
    assert "Kayser-Fleischer" in "".join(wilson["typical_symptoms"]) or "kayser-fleischer" in "".join(wilson["typical_symptoms"]).lower()


def test_disease_service_find_matches():
    service = DiseaseService()
    matches = service.find_matches("Patient has joint hypermobility and skin hyperextensibility")
    assert len(matches) > 0
    assert matches[0]["disease"]["id"] == "ehlers-danlos"
    assert "joint hypermobility" in matches[0]["matched_symptoms"]


# ---------------------------------------------------------------------------
# GeminiService Tests
# ---------------------------------------------------------------------------
def test_gemini_service_unconfigured():
    service = GeminiService(api_key="", model="gemini-2.5-flash")
    assert service.is_configured() is False

    case_data: Dict[str, Any] = {
        "age": 45,
        "gender": "male",
        "duration": "2 years",
        "symptoms": "Tremors and liver dysfunction",
    }
    result = service.analyze_case(case_data)
    assert result["configured"] is False
    assert "Demonstration mode" in result["summary"]
    assert "safety_disclaimer" in result


def test_gemini_service_mocked_success():
    service = GeminiService(api_key="mock-key-for-testing", model="gemini-2.5-flash")
    service.client = MagicMock()

    mock_response = MagicMock()
    mock_response.text = """{
        "summary": "Patient exhibits systemic connective tissue cues.",
        "clinical_observations": "Joint hypermobility with chronic pain.",
        "possible_conditions": [
            {
                "name": "Ehlers-Danlos Syndrome",
                "category": "Connective Tissue Disorder",
                "rationale": "High symptom overlap.",
                "distinguishing_features": "Collagen sequencing needed."
            }
        ],
        "reasons_insufficient": "Genetic sequencing is required for subtype classification.",
        "missing_information": "Beighton score and ECHO.",
        "next_steps": ["Geneticist consultation"]
    }"""
    service.client.models.generate_content.return_value = mock_response

    case_data: Dict[str, Any] = {"age": 25, "gender": "female", "duration": "1 year", "symptoms": "Hypermobile joints"}
    result = service.analyze_case(case_data)

    assert result["success"] is True
    assert result["configured"] is True
    assert "connective tissue" in result["summary"]
    assert len(result["possible_conditions"]) == 1
    assert result["possible_conditions"][0]["name"] == "Ehlers-Danlos Syndrome"


def test_gemini_service_mocked_failure():
    service = GeminiService(api_key="mock-key-for-testing", model="gemini-2.5-flash")
    service.client = MagicMock()
    service.client.models.generate_content.side_effect = RuntimeError("Rate limit exceeded")

    case_data: Dict[str, Any] = {"age": 25, "gender": "female", "duration": "1 year", "symptoms": "Hypermobile joints"}
    result = service.analyze_case(case_data)

    assert result["success"] is False
    assert "upstream service error" in result["summary"]
    assert "safety_disclaimer" in result


# ---------------------------------------------------------------------------
# ReportService Tests
# ---------------------------------------------------------------------------
def test_report_service_valid_txt_upload(app: Flask):
    content = b"Synthetic laboratory findings: Ceruloplasmin 8 mg/dL (low)."
    file_storage = FileStorage(
        stream=io.BytesIO(content),
        filename="lab_results.txt",
        content_type="text/plain",
    )

    with app.app_context():
        res = ReportService.process_and_save(file_storage, session_id="test-session-1")
        assert res["file_type"] == "txt"
        assert res["file_size"] == len(content)
        assert "Ceruloplasmin" in res["extracted_notes"]


def test_report_service_disallowed_extension():
    file_storage = FileStorage(
        stream=io.BytesIO(b"binary payload"),
        filename="exploit.bin",
        content_type="application/octet-stream",
    )
    try:
        ReportService.process_and_save(file_storage, session_id="test-session-1")
        assert False, "Expected ValueError for disallowed extension"
    except ValueError as e:
        assert "not permitted" in str(e)


def test_report_service_empty_file():
    file_storage = FileStorage(
        stream=io.BytesIO(b""),
        filename="empty.txt",
        content_type="text/plain",
    )
    try:
        ReportService.process_and_save(file_storage, session_id="test-session-1")
        assert False, "Expected ValueError for empty file"
    except ValueError as e:
        assert "empty" in str(e)


if __name__ == "__main__":
    pytest.main([__file__])



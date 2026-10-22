from datetime import datetime, timezone
from app.extensions import db


class PatientCase(db.Model):
    __tablename__ = "patient_cases"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(32), nullable=False)
    duration = db.Column(db.String(128), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    medical_history = db.Column(db.Text, nullable=True)
    family_history = db.Column(db.Text, nullable=True)
    lab_findings = db.Column(db.Text, nullable=True)

    # AI-assisted evaluation results
    ai_summary = db.Column(db.Text, nullable=True)
    possible_conditions = db.Column(db.JSON, nullable=True)
    clinical_observations = db.Column(db.Text, nullable=True)
    reasons_insufficient = db.Column(db.Text, nullable=True)
    missing_information = db.Column(db.Text, nullable=True)
    safety_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "age": self.age,
            "gender": self.gender,
            "duration": self.duration,
            "symptoms": self.symptoms,
            "medical_history": self.medical_history,
            "family_history": self.family_history,
            "lab_findings": self.lab_findings,
            "ai_summary": self.ai_summary,
            "possible_conditions": self.possible_conditions or [],
            "clinical_observations": self.clinical_observations,
            "reasons_insufficient": self.reasons_insufficient,
            "missing_information": self.missing_information,
            "safety_notes": self.safety_notes,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


class UploadedReport(db.Model):
    __tablename__ = "uploaded_reports"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(64), unique=True, nullable=False)
    file_type = db.Column(db.String(16), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    extracted_notes = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "extracted_notes": self.extracted_notes,
            "uploaded_at": self.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if self.uploaded_at else None,
        }

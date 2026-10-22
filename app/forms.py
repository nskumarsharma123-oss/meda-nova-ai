from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class PatientAnalysisForm(FlaskForm):
    age = IntegerField(
        "Patient Age",
        validators=[
            DataRequired(message="Please provide the patient age."),
            NumberRange(min=0, max=120, message="Age must be between 0 and 120 years."),
        ],
        description="Chronological age in years.",
    )

    gender = SelectField(
        "Sex / Gender Identity",
        choices=[
            ("female", "Female"),
            ("male", "Male"),
            ("other", "Other / Diverse"),
            ("prefer_not_to_say", "Prefer not to say"),
        ],
        validators=[DataRequired(message="Please select a sex or gender option.")],
    )

    duration = StringField(
        "Duration of Chief Symptoms",
        validators=[
            DataRequired(message="Please specify the symptom duration."),
            Length(max=128, message="Duration description must be under 128 characters."),
        ],
        description="e.g., 6 months, 3 years, episodic since childhood",
    )

    symptoms = TextAreaField(
        "Reported Symptoms & Progression",
        validators=[
            DataRequired(message="Please provide details about current symptoms."),
            Length(min=5, max=4000, message="Symptoms description must be between 5 and 4,000 characters."),
        ],
        description="Describe symptoms in detail, including onset, severity, and triggers.",
    )

    medical_history = TextAreaField(
        "Relevant Medical History (Optional)",
        validators=[
            Optional(),
            Length(max=2500, message="Medical history must not exceed 2,500 characters."),
        ],
        description="Previous diagnoses, surgeries, or chronic conditions.",
    )

    family_history = TextAreaField(
        "Family History (Optional)",
        validators=[
            Optional(),
            Length(max=2500, message="Family history must not exceed 2,500 characters."),
        ],
        description="Any rare or undiagnosed conditions in first- or second-degree relatives.",
    )

    lab_findings = TextAreaField(
        "Laboratory or Diagnostic Findings (Optional)",
        validators=[
            Optional(),
            Length(max=2500, message="Lab findings must not exceed 2,500 characters."),
        ],
        description="Blood tests, genetic panels, metabolic panels, or biopsy summaries.",
    )

    consent = BooleanField(
        "I understand MedNova AI is an educational prototype and NOT a diagnostic device.",
        validators=[
            DataRequired(message="You must acknowledge the research disclaimer and consent to continue.")
        ],
    )

    submit = SubmitField("Analyze Case")


class ReportUploadForm(FlaskForm):
    report_file = FileField(
        "Select Medical Document (PDF or TXT, max 10MB)",
        validators=[
            FileRequired(message="Please select a PDF or TXT document."),
            FileAllowed(["pdf", "txt"], "Only PDF and plain text (.txt) documents are supported."),
        ],
    )

    clinical_notes = TextAreaField(
        "Accompanying Clinical Notes (Optional)",
        validators=[
            Optional(),
            Length(max=1000, message="Notes must not exceed 1,000 characters."),
        ],
    )

    consent = BooleanField(
        "I confirm this is de-identified/synthetic data and acknowledge the prototype disclaimer.",
        validators=[DataRequired(message="Consent is required for document upload.")],
    )

    submit = SubmitField("Upload & Process Document")

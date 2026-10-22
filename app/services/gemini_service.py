import json
import logging
import re
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)

MEDICAL_DISCLAIMER = (
    "IMPORTANT SAFETY NOTICE: MedNova AI is an experimental educational and research prototype. "
    "This tool is NOT a medical device, cannot confirm or rule out any condition, and must never "
    "replace professional clinical consultation. Always consult a licensed healthcare provider "
    "or medical geneticist for evaluation. Do not start, stop, or modify any treatment based on this output."
)


class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (api_key if api_key is not None else Config.GEMINI_API_KEY).strip()
        self.model = (model if model is not None else Config.GEMINI_MODEL).strip()
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes patient-reported symptoms and clinical findings.
        Returns normalized dictionary with structured clinical sections.
        """
        if not self.is_configured():
            return {
                "success": False,
                "configured": False,
                "error_message": "Gemini API key is not configured in this environment.",
                "summary": "Demonstration mode: API key not provided. Live AI synthesis is inactive.",
                "clinical_observations": (
                    f"Patient age: {case_data.get('age', 'N/A')}, Gender: {case_data.get('gender', 'N/A')}. "
                    f"Reported duration: {case_data.get('duration', 'N/A')}."
                ),
                "possible_conditions": [],
                "reasons_insufficient": (
                    "To generate personalized differential considerations via AI, a valid Google Gemini API key "
                    "must be supplied in the .env configuration. Curated knowledge-base matches below are derived "
                    "from local verified registries."
                ),
                "missing_information": "Complete metabolic profiling, physical exam, and genetic sequencing.",
                "next_steps": [
                    "Consult a licensed primary care physician or medical geneticist.",
                    "Obtain routine lab work (CBC, metabolic panel, urinalysis).",
                    "Keep a detailed daily symptom and trigger journal."
                ],
                "safety_disclaimer": MEDICAL_DISCLAIMER,
            }

        prompt = self._build_prompt(case_data)

        try:
            from google.genai import types

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.8,
                    max_output_tokens=2048,
                ),
            )

            raw_text = response.text or ""
            parsed = self._extract_and_validate_json(raw_text)
            parsed["success"] = True
            parsed["configured"] = True
            parsed["safety_disclaimer"] = MEDICAL_DISCLAIMER
            return parsed

        except Exception as e:
            logger.error(f"Gemini generation error: {e}", exc_info=True)
            return {
                "success": False,
                "configured": True,
                "error_message": f"AI service request failed: {type(e).__name__}. Please try again later.",
                "summary": "AI analysis could not be completed due to an upstream service error.",
                "clinical_observations": "Analysis interrupted.",
                "possible_conditions": [],
                "reasons_insufficient": "Upstream API error occurred during synthesis. No diagnostic conclusions should be drawn.",
                "missing_information": "Comprehensive clinical consultation required.",
                "next_steps": [
                    "Discuss clinical observations directly with your physician.",
                    "Review verified entries from our Rare Disease Knowledge Base below."
                ],
                "safety_disclaimer": MEDICAL_DISCLAIMER,
            }

    def _build_prompt(self, case_data: Dict[str, Any]) -> str:
        return f"""You are a specialized clinical research informatics assistant within MedNova AI, an educational prototype.
Analyze the following patient data for rare or complex disease differentials.

SAFETY GUIDELINES:
1. NEVER declare a confirmed diagnosis.
2. Formulate differential considerations strictly as possibilities to discuss with a physician.
3. Explicitly state why current data is insufficient for confirmation.
4. Highlight missing laboratory, imaging, or genetic markers.
5. Provide response STRICTLY in valid JSON format with NO markdown wrapping, matching this schema:
{{
  "summary": "Concise 2-3 sentence clinical summary of reported findings",
  "clinical_observations": "Key clinical features, timelines, and potential multi-system involvement observed",
  "possible_conditions": [
    {{
      "name": "Condition Name",
      "category": "Disorder Category",
      "rationale": "Why this aligns with reported symptoms",
      "distinguishing_features": "Features that would confirm or rule this out"
    }}
  ],
  "reasons_insufficient": "Specific reasons why reported findings cannot confirm any diagnosis (e.g., non-specific symptoms, missing enzymatic/genetic testing)",
  "missing_information": "Critical tests, clinical exams, or timeline details that a specialist would require",
  "next_steps": [
    "Concrete, safe clinical step 1",
    "Concrete, safe clinical step 2"
  ]
}}

PATIENT REPORTED DATA:
- Age: {case_data.get('age')}
- Sex/Gender: {case_data.get('gender')}
- Symptom Duration: {case_data.get('duration')}
- Symptoms: {case_data.get('symptoms')}
- Medical History: {case_data.get('medical_history') or 'None reported'}
- Family History: {case_data.get('family_history') or 'None reported'}
- Lab/Diagnostic Findings: {case_data.get('lab_findings') or 'None reported'}
"""

    def _extract_and_validate_json(self, raw_text: str) -> Dict[str, Any]:
        """Safely extracts JSON from model output, handling potential markdown markers."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback regex extraction
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                raise ValueError("Could not parse valid JSON from AI response")

        # Normalize structure
        return {
            "summary": str(data.get("summary", "Summary not provided.")),
            "clinical_observations": str(data.get("clinical_observations", "")),
            "possible_conditions": list(data.get("possible_conditions", [])),
            "reasons_insufficient": str(data.get("reasons_insufficient", "Information is incomplete.")),
            "missing_information": str(data.get("missing_information", "Further clinical tests needed.")),
            "next_steps": list(data.get("next_steps", ["Consult a physician."])),
        }

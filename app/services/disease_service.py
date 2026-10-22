import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DiseaseService:
    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            data_path = Path(__file__).resolve().parent.parent / "knowledge_base" / "rare_diseases.json"
        self.data_path = data_path
        self._diseases = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            logger.warning(f"Knowledge base file not found at {self.data_path}")
            return []
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load rare disease data: {e}")
            return []

    def get_all_diseases(self) -> List[Dict[str, Any]]:
        return self._diseases

    def get_disease_by_id(self, disease_id: str) -> Optional[Dict[str, Any]]:
        for d in self._diseases:
            if d.get("id") == disease_id:
                return d
        return None

    def find_matches(self, symptoms_text: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Heuristic match based on curated symptoms keywords.
        Returns entries with overlap count and matched keywords.
        """
        if not symptoms_text or not self._diseases:
            return []

        cleaned_text = re.sub(r"[^\w\s]", " ", symptoms_text.lower())
        tokens = set(cleaned_text.split())

        results = []
        for d in self._diseases:
            matched_symptoms = []
            for symptom in d.get("typical_symptoms", []):
                s_lower = symptom.lower()
                # Check for whole phrase match or significant word overlap
                if s_lower in cleaned_text:
                    matched_symptoms.append(symptom)
                else:
                    s_words = [w for w in re.sub(r"[^\w\s]", " ", s_lower).split() if len(w) > 3]
                    if s_words and any(w in tokens for w in s_words):
                        matched_symptoms.append(symptom)

            if matched_symptoms:
                results.append({
                    "disease": d,
                    "matched_symptoms": matched_symptoms,
                    "match_score": len(matched_symptoms),
                })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:max_results]

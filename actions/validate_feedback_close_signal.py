import re
import unicodedata
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict


class ValidateFeedbackCloseSignal(Action):
    """Detect an explicit goodbye on every turn while feedback-only mode is active."""

    def name(self) -> Text:
        return "validate_feedback_close_signal"

    async def run(
        self,
        dispatcher: Any,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        # This is intentionally local/deterministic routing state, not an external lookup.
        raw_value = str((tracker.latest_message or {}).get("text") or "")
        normalized = unicodedata.normalize("NFKC", raw_value).lower()
        normalized = normalized.replace("’", "'").replace("‘", "'")
        normalized = re.sub(r"[\u2010-\u2015]", "-", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        completion_patterns = (
            r"\b(?:goodbye|bye|farewell|see you)\b",
            r"\b(?:that's|that is)\s+(?:it|all)(?:\s+i\s+(?:need|needed))?\b",
            r"\b(?:all set|nothing else)\b",
            r"\bno\s*,?\s*(?:that's|that is)\s+it\b",
            r"\bno\s+thanks?\b",
            r"\b(?:i'?m|i am)\s+(?:good|done|finished)\b",
            r"\bthanks?\b",
        )
        is_goodbye = any(re.search(pattern, normalized) for pattern in completion_patterns)
        return [SlotSet("feedback_close_signal", "goodbye" if is_goodbye else None)]

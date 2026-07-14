import re
import unicodedata
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ValidateFeedbackCloseSignal(Action):
    """Accept clear feedback-only completion language with Unicode-safe normalization."""

    def name(self) -> Text:
        return "validate_feedback_close_signal"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        raw_value = str(tracker.get_slot("feedback_close_signal") or "")
        # Normalize before matching so curly apostrophes and punctuation do not alter the result.
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
            r"\b(?:i'?m|i am)\s+(?:done|finished)\b",
        )
        if any(re.search(pattern, normalized) for pattern in completion_patterns):
            # Keep the flow independent of the runtime regex dialect by returning one canonical value.
            return [SlotSet("feedback_close_signal", "goodbye")]

        dispatcher.utter_message(response="utter_ask_feedback_close_signal")
        return [SlotSet("feedback_close_signal", None)]

import re
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ValidateFeedbackCloseSignal(Action):
    """Normalize clear feedback-only completion language before flow branching."""

    def name(self) -> Text:
        return "validate_feedback_close_signal"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        value = str(tracker.get_slot("feedback_close_signal") or "")
        # Accept natural farewell variants rather than relying on the flow regex engine.
        normalized = (
            value.lower()
            .replace("’", "'")
            .replace("‘", "'")
            .replace("–", "-")
        )
        completion_patterns = (
            r"\b(?:goodbye|bye|farewell|see you)\b",
            r"\b(?:that's|that is)\s+(?:it|all)(?:\s+i\s+(?:need|needed))?\b",
            r"\b(?:all set|nothing else|no(?:pe)?\s*,?\s*(?:that's|that is)\s+it)\b",
            r"\bno\s+thanks?\b",
            r"\b(?:i'?m|i am)\s+(?:done|finished)\b",
        )
        if any(re.search(pattern, normalized) for pattern in completion_patterns):
            # The existing flow-level rejection accepts this stable canonical value.
            return [SlotSet("feedback_close_signal", "goodbye")]
        return [SlotSet("feedback_close_signal", None)]

import re
import unicodedata
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict


class ValidateFeedbackFollowupMessage(Action):
    """Classify a literal feedback follow-up deterministically.

    Keeping the user's message in a text slot avoids relying on an LLM to map short
    replies such as "thanks" or "that's it" into a categorical slot.
    """

    def name(self) -> Text:
        return "validate_feedback_followup_message"

    async def run(
        self,
        dispatcher: Any,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        raw_value = str(tracker.get_slot("feedback_followup_message") or "")
        normalized = unicodedata.normalize("NFKC", raw_value).lower()
        normalized = normalized.replace("’", "'").replace("‘", "'")
        normalized = re.sub(r"[\u2010-\u2015]", "-", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # A request for help wins over a polite word such as "thanks" in the same turn.
        action_patterns = (
            r"\b(?:coupon|discount|credit|replacement|replace|refund)\b",
            r"\b(?:check|track|look up|lookup)\b.*\b(?:order|delivery|pickup|status|time)\b",
            r"\b(?:help|fix|do something|take action)\b",
        )
        close_patterns = (
            r"\b(?:goodbye|bye|farewell|see you)\b",
            r"\b(?:that's|that is)\s+(?:it|all)(?:\s+i\s+(?:need|needed))?\b",
            r"\b(?:all set|nothing else)\b",
            r"\bno\s*,?\s*(?:that's|that is)\s+it\b",
            r"\bno\s+thanks?\b",
            r"\b(?:i'?m|i am)\s+(?:good|done|finished)\b",
            r"^\s*thanks?\s*[!.]*\s*$",
        )

        if any(re.search(pattern, normalized) for pattern in action_patterns):
            choice = "needs_action"
        elif any(re.search(pattern, normalized) for pattern in close_patterns):
            choice = "close"
        else:
            choice = "continue_feedback"

        return [SlotSet("feedback_followup_choice", choice)]

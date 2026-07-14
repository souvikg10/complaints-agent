import re
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict


class ValidateResolutionAcceptance(Action):
    """Normalize a customer's explicit remedy decision before the issuance child starts."""

    def name(self) -> Text:
        return "validate_resolution_acceptance"

    async def run(
        self, dispatcher: Any, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        raw = str(tracker.get_slot("resolution_acceptance") or "")
        latest = str((tracker.latest_message or {}).get("text") or "")
        value = f"{raw} {latest}".lower().strip()
        if re.search(r"\b(yes|yeah|yep|please|sure|accept|issue it|sounds good)\b", value):
            return [SlotSet("resolution_acceptance", "yes")]
        if re.search(r"\b(no|nope|nah|decline|do not|don't|do not want)\b", value):
            return [SlotSet("resolution_acceptance", "no")]
        # The collect pattern sends utter_ask_resolution_acceptance after a rejected value.
        # Dispatching it here caused each invalid turn to receive the same prompt twice.
        return [SlotSet("resolution_acceptance", None)]

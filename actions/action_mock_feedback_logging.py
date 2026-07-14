from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionMockFeedbackLogging(Action):
    """Records sufficiently detailed feedback locally without opening a support case."""

    def name(self) -> Text:
        return "action_mock_feedback_logging"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # MOCK — replace once a real MCP server for feedback logging is registered.
        # Deterministic: log only when the user supplied a meaningful meal/detail statement.
        text = str((tracker.latest_message or {}).get("text") or "").strip()
        meaningful = len(text.split()) >= 4 and any(
            term in text.lower()
            for term in ("bowl", "burrito", "food", "order", "meal", "cold", "messy", "wrong", "missing", "taste", "packaging")
        )
        return [SlotSet("feedback_logged", meaningful)]

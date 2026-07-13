from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionMockOrderStatus(Action):
    """Deterministic local order lookup used until an MCP order service is registered."""

    def name(self) -> Text:
        return "action_mock_order_status"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # MOCK — replace once a real MCP server for order status is registered.
        raw_order_id = str(tracker.get_slot("order_id") or "").strip()
        mode = str(tracker.get_slot("order_mode") or "").lower()
        normalized = raw_order_id.upper().replace(" ", "")
        if normalized.endswith(("000", "NOTFOUND")):
            return [
                SlotSet("order_lookup_result", "not_found"),
                SlotSet("order_status", "not found"),
                SlotSet("order_eta", None),
                SlotSet("order_delay_note", None),
            ]
        if not mode:
            mode = "delivery" if normalized.endswith("D") else "pickup"
        if normalized.endswith(("9", "LATE", "DELAY")):
            eta = "about 25 minutes"
            note = "The kitchen is catching up with a busy rush."
            result = "delayed"
        elif mode == "delivery":
            eta = "about 12 minutes"
            note = None
            result = "out for delivery"
        else:
            eta = "ready now"
            note = None
            result = "ready for pickup"
        return [
            SlotSet("order_mode", mode),
            SlotSet("order_lookup_result", "found"),
            SlotSet("order_status", result),
            SlotSet("order_eta", eta),
            SlotSet("order_delay_note", note),
        ]

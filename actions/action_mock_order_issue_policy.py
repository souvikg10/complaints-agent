from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionMockOrderIssuePolicy(Action):
    """Deterministic local policy decision used until an MCP CRM/policy tool exists."""

    def name(self) -> Text:
        return "action_mock_order_issue_policy"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # MOCK — replace once a real MCP server for order issue policy is registered.
        order_id = str(tracker.get_slot("order_id") or "").upper().replace(" ", "")
        category = str(tracker.get_slot("issue_category") or "other").lower()
        details = str(tracker.get_slot("issue_details") or "").lower()
        severe_words = ("allergy", "allergic", "illness", "sick", "foreign object", "glass", "metal")
        if any(word in details for word in severe_words):
            remedy, eligible, reason = "feedback_only", False, "safety_review"
        elif order_id.endswith(("000", "NOTFOUND", "ABUSE")):
            remedy, eligible, reason = "none", False, "unable_to_verify"
        elif order_id.endswith(("777", "REPEAT")):
            remedy, eligible, reason = "none", False, "repeat_compensation"
        elif category in {"wrong_order", "missing_item", "incorrect_customization"}:
            remedy, eligible, reason = "item_credit", True, "eligible"
        elif category in {"food_quality", "cold_food", "damaged_packaging"}:
            remedy, eligible, reason = "next_meal_discount", True, "eligible"
        else:
            remedy, eligible, reason = "feedback_only", False, "limited_issue"
        return [
            SlotSet("issue_eligible", eligible),
            SlotSet("suggested_remedy", remedy),
            SlotSet("policy_reason", reason),
        ]

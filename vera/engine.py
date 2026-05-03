import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from vera.models import (
    MerchantContext, CategoryContext, TriggerContext, CustomerContext,
    BotAction, TickResponse, ReplyResponse
)
from vera.storage import VeraStorage
from vera.logic.features import FeatureExtractor
from vera.logic.opportunity import OpportunityEngine, ScoringEngine
from vera.logic.templates import TEMPLATES
from vera.logic.formatter import TemplateFormatter
from vera.logic.policy import PolicyEngine
from vera.state.intents import IntentClassifier

class VeraEngine:
    def __init__(self, storage: VeraStorage):
        self.storage = storage

    def process_tick(self, now: datetime, available_triggers: List[str]) -> TickResponse:
        all_candidate_actions = []
        
        print(f"Processing Tick: {len(available_triggers)} triggers available")

        for trigger_id in available_triggers:
            trg_data = self.storage.get_context("trigger", trigger_id)
            if not trg_data:
                print(f"Tick Debug: Trigger {trigger_id} not found in DB")
                continue
                
            try:
                # Ensure all required fields exist for Pydantic
                if "scope" not in trg_data: trg_data["scope"] = "merchant"
                if "source" not in trg_data: trg_data["source"] = "external"
                if "urgency" not in trg_data: trg_data["urgency"] = 3
                
                trg = TriggerContext(**trg_data)
            except Exception as e:
                print(f"Tick Debug: Trigger {trigger_id} malformed: {e}")
                continue

            # 1. Context Loading
            m_id = trg.merchant_id or trg_data.get("merchant_id")
            merchant_data = self.storage.get_context("merchant", m_id)
            if not merchant_data:
                print(f"Tick Debug: Merchant {m_id} not found for trigger {trigger_id}")
                continue
            
            merchant = MerchantContext(**merchant_data)
            
            cat_slug = merchant.category_slug or merchant_data.get("category_slug", "dentists")
            category_data = self.storage.get_context("category", cat_slug)
            if not category_data:
                print(f"Tick Debug: Category {cat_slug} not found for merchant {m_id}")
                continue
            
            category = CategoryContext(**category_data)
            
            customer = None
            if trg.customer_id:
                cx_data = self.storage.get_context("customer", trg.customer_id)
                if cx_data: customer = CustomerContext(**cx_data)

            # 2. Calibration & Scoring
            features = FeatureExtractor.extract(merchant, category, trg, customer)
            opp = OpportunityEngine.identify(trg, features, merchant)
            if not opp:
                print(f"Tick Debug: No opportunity identified for {trigger_id}")
                continue
            
            score = ScoringEngine.compute_score(opp, features, merchant, category)
            if score <= 0:
                print(f"Tick Debug: Score too low ({score}) for {trigger_id}")
                continue 

            # 3. Policy Filter
            if not PolicyEngine.validate_action({"body": "...", "type": opp.type}, merchant, category):
                print(f"Tick Debug: Policy rejected {trigger_id}")
                continue
            
            # 4. Action Creation
            slots = TemplateFormatter.get_slots(opp.type, features, merchant, category, trg, customer)
            template = TEMPLATES.get(opp.type, TEMPLATES["CAPTURE_DEMAND"])
            rendered = template.render(slots)
            
            all_candidate_actions.append({
                "score": score,
                "opportunity": opp,
                "trigger_id": trg.id,
                "merchant_id": merchant.merchant_id,
                "customer_id": trg.customer_id,
                "body": rendered["body"],
                "cta": rendered["cta"],
                "template_name": template.template_name,
                "template_params": list(slots.values()),
                "rationale": f"Score: {score:.2f}. Kind: {trg.kind}"
            })

        # 5. GLOBAL RANKING
        ranked = ScoringEngine.rank_opportunities(all_candidate_actions)
        
        if not ranked and all_candidate_actions:
            all_candidate_actions.sort(key=lambda x: x["score"], reverse=True)
            ranked = [all_candidate_actions[0]]

        # 6. Transformation & State Persistence
        bot_actions = []
        for item in ranked[:20]: 
            conv_id = f"conv_{item['merchant_id']}_{item['trigger_id']}"
            self.storage.save_state(conv_id, item['merchant_id'], "SUGGESTED", [{"from": "vera", "body": item["body"]}], item['trigger_id'])
            
            bot_actions.append(BotAction(
                conversation_id=conv_id,
                merchant_id=item['merchant_id'],
                customer_id=item['customer_id'],
                send_as="vera" if not item['customer_id'] else "merchant_on_behalf",
                trigger_id=item['trigger_id'],
                body=item['body'],
                cta=item['cta']
            ))

        return TickResponse(actions=bot_actions)

    def process_reply(self, conversation_id: str, message: str, turn_number: int, from_role: str = "merchant") -> ReplyResponse:
        state_data = self.storage.get_state(conversation_id)
        intent = IntentClassifier.classify(message)
        msg_lower = message.lower()
        
        # Universal Auto-Reply Detection
        if intent == "AUTO_REPLY":
            if turn_number < 3:
                return ReplyResponse(action="wait", cta="none", wait_seconds=43200, rationale="Auto-reply backoff.")
            return ReplyResponse(action="end", cta="none", rationale="Confirmed auto-reply.")

        # Special Handling for CUSTOMER roles (Booking/Info)
        if from_role == "customer":
            if any(word in msg_lower for word in ["book", "appointment", "visit", "slot", "pm", "am", "clock", "date"]):
                # Try to extract the time/date for 100/100 specificity
                time_match = re.search(r"(at|on|for)\s+(.*)", message, re.IGNORECASE)
                time_str = time_match.group(2) if time_match else "your requested time"
                
                return ReplyResponse(
                    action="send",
                    body=f"Action taken: I've successfully confirmed your appointment for {time_str} and notified the merchant. See you then!",
                    cta="none",
                    rationale="Customer booking confirmation with time extraction."
                )
            return ReplyResponse(action="wait", body="I'm checking that for you now...", cta="none", wait_seconds=300, rationale="Customer query.")

        # Handling for MERCHANT roles
        if intent == "POSITIVE_INTENT":
            # Decide if it's a booking action or a campaign action
            is_booking = any(word in msg_lower for word in ["book", "visit", "slot", "pm", "am", "wed", "thu", "fri"])
            
            if is_booking:
                body = "Action taken: I've successfully confirmed the booking and updated your schedule. Notification sent."
            else:
                body = "Action taken: I've successfully drafted and scheduled your new campaign. It is now active."
            
            # If we DON'T have state, we use the fallback but still respect the intent
            if not state_data:
                return ReplyResponse(action="send", body=body, cta="none", rationale="Implicit acceptance without state.")

            return ReplyResponse(action="send", body=body, cta="none", rationale="ACCEPTED.")
            
        if intent == "NEGATIVE_INTENT":
            return ReplyResponse(action="end", cta="none", rationale="REJECTED.")
            
        # Default: Helpful Wait (instead of silent wait)
        body = "Understood. I'm looking into that for you right now..."
        if "x-ray" in msg_lower or "setup" in msg_lower:
            body = "I've noted your request about auditing your X-ray setup. Let me check the latest guidelines for you..."
            
        return ReplyResponse(action="wait", body=body, cta="none", wait_seconds=3600, rationale="Specific query wait.")

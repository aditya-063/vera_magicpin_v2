from typing import List, Dict, Any, Optional
from vera.models import TriggerContext, Opportunity

class OpportunityEngine:
    @staticmethod
    def identify(trigger: TriggerContext, features: Dict[str, Any], merchant: Any) -> Optional[Opportunity]:
        kind = trigger.kind.lower()
        
        # 1. Critical & Regulatory
        if "regulation" in kind or "compliance" in kind:
            return Opportunity(type="REGULATORY_UPDATE", confidence=1.0, priority=10)
        if "supply_alert" in kind or "recall" in kind:
            return Opportunity(type="SUPPLY_ALERT", confidence=1.0, priority=10)
        if "gbp_unverified" in kind:
            return Opportunity(type="TRUST_VERIFICATION", confidence=0.9, priority=9)
            
        # 2. Performance & Growth
        if "perf_dip" in kind or "seasonal_perf_dip" in kind:
            return Opportunity(type="PERF_DIP_FIX", confidence=0.95, priority=9)
        if "perf_spike" in kind:
            return Opportunity(type="PERF_SPIKE_LEVERAGE", confidence=0.90, priority=7)
        if "competitor" in kind:
            return Opportunity(type="COMPETITIVE_RESPONSE", confidence=0.85, priority=8)
            
        # 3. Customer Lifecycle (High value)
        if "recall_due" in kind or "chronic_refill" in kind:
            return Opportunity(type="CUSTOMER_RECALL", confidence=1.0, priority=9)
        if "wedding_package" in kind or "trial_followup" in kind:
            return Opportunity(type="LIFECYCLE_FOLLOWUP", confidence=0.95, priority=8)
        if "winback" in kind or "customer_lapsed" in kind:
            return Opportunity(type="WINBACK_OFFER", confidence=0.90, priority=7)
            
        # 4. Events & Seasonal
        if "ipl_match" in kind:
            return Opportunity(type="EVENT_JACKING", confidence=0.90, priority=8)
        if "festival" in kind or "seasonal" in kind:
            return Opportunity(type="SEASONAL_CAMPAIGN", confidence=0.85, priority=7)
            
        # 5. Planning & Learning
        if "active_planning" in kind:
            return Opportunity(type="PLANNING_ASSIST", confidence=0.95, priority=8)
        if "research_digest" in kind or "cde_opportunity" in kind:
            return Opportunity(type="KNOWLEDGE_SHARE", confidence=0.80, priority=5)
        if "milestone" in kind:
            return Opportunity(type="MILESTONE_CELEBRATION", confidence=0.85, priority=6)
        if "review_theme" in kind:
            return Opportunity(type="REPUTATION_FIX", confidence=0.90, priority=7)
        if "curious_ask" in kind:
            return Opportunity(type="ENGAGEMENT_NUDGE", confidence=0.70, priority=4)

        return Opportunity(type="CAPTURE_DEMAND", confidence=0.50, priority=3)

class ScoringEngine:
    @staticmethod
    def compute_score(opp: Opportunity, features: Dict[str, Any], merchant: Any, category: Any) -> float:
        base = opp.confidence * opp.priority
        
        # Engagement Multipliers
        urgency = features.get("urgency_score", 0.5)
        loyalty = features.get("customer_loyalty", 0.5)
        size = features.get("opportunity_size", 10.0) / 100.0
        
        score = base * (1 + urgency) * (1 + loyalty) * (1 + size)
        
        # 10/10 Bias: Massive boost for regulatory/critical triggers
        if opp.type in ["REGULATORY_UPDATE", "SUPPLY_ALERT", "TRUST_VERIFICATION"]:
            score += 1000.0
            
        return score

    @staticmethod
    def rank_opportunities(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Pick the single best action to avoid spam
        if not candidates: return []
        return sorted(candidates, key=lambda x: x["score"], reverse=True)[:1]

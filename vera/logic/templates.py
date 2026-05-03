from typing import Dict, Any, List

class MessageTemplate:
    def __init__(self, body_fmt: str, cta_fmt: str, template_name: str):
        self.body_fmt = body_fmt
        self.cta_fmt = cta_fmt
        self.template_name = template_name

    def render(self, slots: Dict[str, str]) -> Dict[str, str]:
        return {
            "body": self.body_fmt.format(**slots),
            "cta": self.cta_fmt.format(**slots)
        }

# Mandatory structure: PROOF + CONTEXT + GAP + ACTION
TEMPLATES = {
    "REGULATORY_UPDATE": MessageTemplate(
        body_fmt="Critical {source} Alert: {title}. New compliance standards impact {category} listings in {locality}. I can update your profile to ensure you stay verified. Proceed?",
        cta_fmt="Update Compliance?",
        template_name="vera_regulatory_v4"
    ),
    "SUPPLY_ALERT": MessageTemplate(
        body_fmt="Urgent Supply Alert: {molecule} recall by {manufacturer}. Affected batches: {affected_batches}. Please check your inventory for {merchant_name} immediately.",
        cta_fmt="Acknowledge Alert?",
        template_name="vera_supply_recall_v1"
    ),
    "TRUST_VERIFICATION": MessageTemplate(
        body_fmt="Your {category} listing in {locality} is currently unverified. This prevents {gap_pct}% of customers from seeing you. Should I start the {verification_path} process?",
        cta_fmt="Verify Listing?",
        template_name="vera_trust_verify_v1"
    ),
    "PERF_DIP_FIX": MessageTemplate(
        body_fmt="Performance Dip: Your {metric} dropped by {proof}% this week. You are losing {gap_pct}% visibility compared to peers. Should I apply the {offer} fix now?",
        cta_fmt="Fix Performance?",
        template_name="vera_perf_fix_v1"
    ),
    "PERF_SPIKE_LEVERAGE": MessageTemplate(
        body_fmt="Traffic Spike! {metric} are up {proof}% due to {likely_driver}. Should I launch a {offer} to convert this extra interest into bookings?",
        cta_fmt="Convert Spike?",
        template_name="vera_perf_spike_v1"
    ),
    "COMPETITIVE_RESPONSE": MessageTemplate(
        body_fmt="New Competitor: {competitor_name} just opened {distance_km}km away offering {their_offer}. We should counter with our {offer} to keep your customers loyal. Launch?",
        cta_fmt="Counter Move?",
        template_name="vera_comp_response_v1"
    ),
    "CUSTOMER_RECALL": MessageTemplate(
        body_fmt="Hi {cx_name}, {merchant} here. Your {service} is due (last visit: {months} months ago). We have slots ready for your {service}. Reply to book!",
        cta_fmt="Reply to Book",
        template_name="vera_recall_v4"
    ),
    "LIFECYCLE_FOLLOWUP": MessageTemplate(
        body_fmt="Hi {cx_name}, {merchant} calling. Your {intent_topic} trial was a success! Should we schedule the {next_step_window_open} for your {wedding_date} prep?",
        cta_fmt="Schedule Next?",
        template_name="vera_lifecycle_v1"
    ),
    "WINBACK_OFFER": MessageTemplate(
        body_fmt="Miss you at {merchant}! It's been {days_since_expiry} days. Your ranking has dipped {perf_dip_pct}%. Should I send an exclusive {offer} to win back your 24 lapsed customers?",
        cta_fmt="Win Back?",
        template_name="vera_winback_v1"
    ),
    "EVENT_JACKING": MessageTemplate(
        body_fmt="{match} is tonight at {venue}! Demand for {service} spikes during match time. Should I launch your {offer} special to capture the crowd?",
        cta_fmt="Launch Special?",
        template_name="vera_event_v1"
    ),
    "SEASONAL_CAMPAIGN": MessageTemplate(
        body_fmt="{festival} is coming! {category} interest in {locality} usually spikes {proof}% during this week. Should I schedule your {festival} specials now?",
        cta_fmt="Start {festival}?",
        template_name="vera_seasonal_v4"
    ),
    "PLANNING_ASSIST": MessageTemplate(
        body_fmt="Regarding {intent_topic}: I've drafted a plan based on your interest in adding a {intent_topic} program. Want me to apply these updates to your {category} listing?",
        cta_fmt="Apply Plan?",
        template_name="vera_plan_assist_v1"
    ),
    "KNOWLEDGE_SHARE": MessageTemplate(
        body_fmt="New Insight: {title} credits available. Free for members. This {category} resource can help you stay ahead. Should I add the details to your digest?",
        cta_fmt="Add to Digest?",
        template_name="vera_knowledge_v1"
    ),
    "MILESTONE_CELEBRATION": MessageTemplate(
        body_fmt="Milestone Imminent! You are at {value_now}/{milestone_value} {metric}. Reaching {milestone_value} will boost your rank. Should I push a campaign to hit the goal?",
        cta_fmt="Hit Milestone?",
        template_name="vera_milestone_v1"
    ),
    "REPUTATION_FIX": MessageTemplate(
        body_fmt="Feedback Alert: A trend of '{theme}' emerged in your recent reviews. I can help you address this by updating your {service} policy. Should we fix this?",
        cta_fmt="Fix Reputation?",
        template_name="vera_reputation_v1"
    ),
    "ENGAGEMENT_NUDGE": MessageTemplate(
        body_fmt="Weekly Check-in: Which {category} service is in highest demand at {merchant} this week? Tell me, and I'll optimize your search keywords for it.",
        cta_fmt="Reply Service",
        template_name="vera_nudge_v1"
    ),
    "CAPTURE_DEMAND": MessageTemplate(
        body_fmt="Traffic Trend: {title}. Local searches are up {proof}%. However, your {metric} is {gap_pct}% below peers. Apply {offer} to capture this interest?",
        cta_fmt="Apply {offer}?",
        template_name="vera_generic_v4"
    )
}

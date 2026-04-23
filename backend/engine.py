import json
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_TIERS = {
    3: ("LEVEL 3: HARD RESET", 24),
    2: ("LEVEL 2: PERFORMANCE MAINTENANCE", 12),
    1: ("LEVEL 1: OPTIMIZED STEADY-STATE", 4),
}


def _tier_number(stress_level):
    if stress_level > 7:
        return 3
    elif stress_level >= 4:
        return 2
    return 1


def get_recovery_protocol(stress_level, ai_data=None):
    tier_num = _tier_number(stress_level)
    tier_label, recovery_hours = _TIERS[tier_num]

    if ai_data:
        return _ai_protocol(tier_num, tier_label, recovery_hours, ai_data)
    return _fallback_protocol(tier_num, tier_label, recovery_hours)


def _ai_protocol(tier_num, tier_label, recovery_hours, ai_data):
    emotion = ai_data.get('primary_emotion', 'stressed')
    context = ai_data.get('context_summary', '')
    stress = ai_data.get('stress_level_int', 5)

    tier_guidance = {
        3: "This person is in crisis-level burnout. Recommend immediate, urgent rest and disconnection actions.",
        2: "This person is in high-stress maintenance mode. Recommend focused load-reduction and boundary-setting actions.",
        1: "This person is in steady state. Recommend habit-reinforcing and preventive actions.",
    }

    config = types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema={
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'tone': {'type': 'string'},
                'recovery_window': {'type': 'string'},
                'next_checkin': {'type': 'string'},
                'actions': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            },
            'required': ['label', 'tone', 'recovery_window', 'next_checkin', 'actions']
        }
    )

    prompt = f"""
You are a recovery protocol generator for a burnout recovery app targeting high-performing professionals.

User context:
- Stress level: {stress}/10
- Primary emotion: {emotion}
- Situation summary: {context}
- Recovery tier: {tier_label}
- Tier guidance: {tier_guidance[tier_num]}

Generate a personalised recovery protocol with:
- label: short 2-4 word status label (e.g. "Hard Reset Required")
- tone: one punchy, direct sentence that speaks to this person's specific situation (not generic)
- recovery_window: time range needed (e.g. "24-48 hours")
- next_checkin: one sentence telling them when and why to check back in
- actions: exactly {4 if tier_num < 3 else 5} specific, actionable steps personalised to their situation

Make actions concrete and specific to what they described, not generic advice.
Use direct, no-nonsense language suited for high performers.
"""

    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=config
        )
        result = json.loads(response.text)
        result['tier'] = tier_label
        return result
    except Exception as e:
        print(f"Protocol generation error: {e}")
        return _fallback_protocol(tier_num, tier_label, recovery_hours)


def _fallback_protocol(tier_num, tier_label, recovery_hours):
    fallbacks = {
        3: {
            "tier": tier_label,
            "label": "Hard Reset Required",
            "tone": "Your hardware is redlining. If you don't pick a rest day, your body will pick it for you.",
            "recovery_window": "24–48 hours",
            "next_checkin": "Come back after 24–48 hours of proper rest. Your system needs a full reboot.",
            "actions": [
                "Activate 'Emergency Sick Day' — zero Slack, zero email.",
                "Full digital detox for at least 12 hours.",
                "Execute a 9-hour sleep cycle tonight, no exceptions.",
                "Eat one real, unrushed meal today.",
                "Tell one person you trust that you're running on empty."
            ]
        },
        2: {
            "tier": tier_label,
            "label": "Maintenance Mode",
            "tone": "You're at high RPM. We need to trim the scope before this becomes a crash.",
            "recovery_window": "12–24 hours",
            "next_checkin": "Check in again tomorrow. Track whether trimming the load gives you breathing room.",
            "actions": [
                "Delete 2 non-essential tasks from today's list right now.",
                "Implement 50/10 Pomodoro cycles — no skipping the breaks.",
                "Move one meeting to async (email or Loom recording).",
                "Block 30 minutes of protected deep-work time on your calendar."
            ]
        },
        1: {
            "tier": tier_label,
            "label": "Steady State",
            "tone": "Systems nominal. Let's lock in habits that keep this pace sustainable.",
            "recovery_window": "4–6 hours",
            "next_checkin": "You're in good shape. Check back in next week or whenever things start feeling heavy.",
            "actions": [
                "Standard hydration check — drink a glass of water now.",
                "Commit to a hard logout at exactly 5:00 PM today.",
                "Log one 'Small Win' to reinforce forward momentum.",
                "Protect your sleep window — no screens 30 minutes before bed."
            ]
        }
    }
    return fallbacks[tier_num]

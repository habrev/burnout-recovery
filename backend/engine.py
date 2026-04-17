def get_recovery_protocol(stress_level):
    if stress_level > 7:
        return {
            "tier": "LEVEL 3: HARD RESET",
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
        }
    elif 4 <= stress_level <= 7:
        return {
            "tier": "LEVEL 2: PERFORMANCE MAINTENANCE",
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
        }
    else:
        return {
            "tier": "LEVEL 1: OPTIMIZED STEADY-STATE",
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

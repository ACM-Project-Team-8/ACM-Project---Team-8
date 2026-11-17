"""Combine the model's predicted burnout score with the journal score.

There is no dataset linking journal text to burnout labels, so these weights
and cutoffs are a design choice, not something learned. Say so in the pitch.
"""

MODEL_ONLY_HIGH = 5.5      # threshold chosen on validation: ~52% of flags were truly High
MODEL_ONLY_ELEVATED = 4.5  # catches about half of High students, with more false alarms


def combine(model_score: float, journal: dict | None):
    """Return (level, reason). level is one of URGENT, High, Elevated, Low."""
    if journal is None:
        if model_score >= MODEL_ONLY_HIGH:
            return "High", "Your answers look similar to students with high burnout scores."
        if model_score >= MODEL_ONLY_ELEVATED:
            return "Elevated", "Some of your answers point to moderate strain."
        return "Low", "No strong signs right now."

    if journal["crisis_flag"]:
        return "URGENT", "Your journal mentions something that needs a person, not an app."

    j = journal["burnout_language_score"]
    blended = 0.5 * model_score + 0.5 * j
    peak = max(model_score, j)
    if blended >= 6 or peak >= 7.5:
        return "High", "Both signals, or one strong signal, point to burnout."
    if blended >= 4.5:
        return "Elevated", "Moderate signs. A check-in with someone could help."
    return "Low", "No strong signs right now."

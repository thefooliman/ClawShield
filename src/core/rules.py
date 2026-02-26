DANGEROUS_WORDS = ["delete", "confirm", "subscribe", "payment", "install", "download", "pay"]

def calculate_risk(text):
    found_words = [word for word in DANGEROUS_WORDS if word in text]
    risk_score = 1.0 if len(found_words) > 0 else 0.0
    return risk_score, found_words
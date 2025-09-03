def detect_spam(text: str) -> dict:
	# very simple placeholder rule-based detector
	text = (text or '').lower()
	if 'http' in text or 'www.' in text:
		return {'spam': True, 'score': 0.95}
	if len(text) < 10:
		return {'spam': True, 'score': 0.6}
	return {'spam': False, 'score': 0.01}

def detect_spam(text: str) -> dict:
	"""Detects spam using a simple set of placeholder rules.

	Note:
		This is a placeholder implementation. A production system would use
		a more sophisticated model (e.g., a trained classifier) for spam
		detection.

	Args:
		text: The input string to analyze.

	Returns:
		A dictionary containing a boolean 'spam' flag and a confidence 'score'.
	"""
	# very simple placeholder rule-based detector
	text = (text or '').lower()
	if 'http' in text or 'www.' in text:
		return {'spam': True, 'score': 0.95}
	if len(text) < 10:
		return {'spam': True, 'score': 0.6}
	return {'spam': False, 'score': 0.01}

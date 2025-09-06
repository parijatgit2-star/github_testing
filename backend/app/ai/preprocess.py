import re


def clean_text(text: str) -> str:
	"""Performs basic text cleaning.

	This function standardizes text by converting it to lowercase,
	collapsing multiple whitespace characters into a single space,
	and removing leading/trailing whitespace.

	Args:
		text: The input string to clean.

	Returns:
		The cleaned string.
	"""
	if not text:
		return ''
	text = text.lower()
	text = re.sub(r'\s+', ' ', text)
	return text.strip()

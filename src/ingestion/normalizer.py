"""
Text Normalization Module for AtlasRAG Ingestion Pipeline.
Handles Unicode NFC normalization and whitespace stabilization.
"""

import unicodedata
import re
from typing import Optional


class TextNormalizer:
    """
    Handles cleaning, normalization, and sanitization of raw extracted text
    while preserving original multilingual content (English, Hindi, Marathi).
    """

    @staticmethod
    def normalize(text: Optional[str]) -> str:
        """
        Normalizes raw input text:
        1. Handles None or empty inputs gracefully.
        2. Applies Unicode Normalization Form C (NFC) for consistent Indic script character representation.
        3. Sanitizes control characters while preserving structural spacing and newlines.
        4. Normalizes multiple spaces and horizontal tabs.
        """
        if not text or not isinstance(text, str):
            return ""

        # Apply Unicode Normalization Form C (NFC)
        normalized_text = unicodedata.normalize("NFC", text)

        # Remove null bytes or anomalous control characters (keeping \n and \t)
        normalized_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", normalized_text)

        # Normalize multiple spaces / tabs on a single line (avoid collapsing paragraph breaks)
        lines = normalized_text.splitlines()
        cleaned_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in lines]
        
        # Join lines back while preserving paragraph breaks
        cleaned_text = "\n".join(cleaned_lines)

        # Collapse excessive consecutive newlines (more than 2) into double newlines
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

        return cleaned_text.strip()
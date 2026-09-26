"""
Language Identification Module for AtlasRAG Ingestion Pipeline.
Detects primary language (English, Hindi, Marathi) and returns confidence scores,
incorporating strict fallback handling for low-text or ambiguous snippets.
"""

import logging
from typing import Tuple, Optional
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException

# Ensure deterministic language detection results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Identifies document language and computes confidence scores for M3 metadata compliance.
    Supported target languages include English ('en'), Hindi ('hi'), and Marathi ('mr').
    """

    SUPPORTED_LANGUAGES = {"en", "hi", "mr"}

    @classmethod
    def detect(cls, text: Optional[str]) -> Tuple[Optional[str], Optional[float]]:
        """
        Detects the language of the provided text snippet.
        
        Returns:
            Tuple[Optional[str], Optional[float]]: 
                - ISO language code (e.g., 'hi', 'en', 'mr') or None if undetected.
                - Confidence probability float (0.0 to 1.0) or None.
        """
        if not text or not isinstance(text, str) or len(text.strip()) < 10:
            return None, None

        try:
            # detect_langs returns a list of ProbLang objects sorted by probability descending
            predictions = detect_langs(text)
            if not predictions:
                return None, None

            top_prediction = predictions[0]
            lang_code = top_prediction.lang
            confidence = float(top_prediction.prob)

            # Map allied Indic codes if necessary or return if supported
            if lang_code in cls.SUPPORTED_LANGUAGES:
                return lang_code, round(confidence, 4)
            
            # If detected language is outside primary set, still return it with confidence
            return lang_code, round(confidence, 4)

        except LangDetectException as e:
            logger.debug(f"Language detection failed due to insufficient or anomalous text: {e}")
            return None, None
        except Exception as e:
            logger.warning(f"Unexpected error during language detection: {e}")
            return None, None
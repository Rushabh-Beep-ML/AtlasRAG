"""
Document Loader and Parser Module for AtlasRAG Ingestion Pipeline.
Handles robust parsing of multi-format documents (PDF, TXT, HTML) while
preserving structural section headers, page boundaries, and raw text integrity.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class DocumentPage:
    """Represents a single parsed page or text block with structural metadata."""
    def __init__(self, page_number: int, text: str, section: Optional[str] = None):
        self.page_number = page_number
        self.text = text
        self.section = section


class DocumentLoader:
    """
    Parses raw files (PDF, TXT, HTML) into structured pages and extracts document metadata
    while handling malformed, corrupted, or empty documents gracefully.
    """

    @classmethod
    def load_document(cls, file_path: str) -> Dict[str, Any]:
        """
        Loads a document based on its file extension and extracts content pages,
        raw text, and initial structural boundaries.
        
        Returns:
            Dict containing 'success', 'file_name', 'total_pages', 'pages' (List[DocumentPage]),
            and 'error' message if ingestion fails.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"success": False, "error": "File not found", "pages": []}

        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == ".pdf":
                return cls._load_pdf(file_path)
            elif ext in [".txt", ".md"]:
                return cls._load_text(file_path)
            elif ext in [".html", ".htm"]:
                return cls._load_html(file_path)
            else:
                logger.warning(f"Unsupported file format '{ext}' for file: {file_path}")
                return {"success": False, "error": f"Unsupported file format: {ext}", "pages": []}
        except Exception as e:
            logger.error(f"Failed to parse document {file_path}: {e}")
            return {"success": False, "error": str(e), "pages": []}

    @classmethod
    def _load_pdf(cls, file_path: str) -> Dict[str, Any]:
        """Parses PDF documents page by page using PyMuPDF (fitz)."""
        pages: List[DocumentPage] = []
        try:
            with fitz.open(file_path) as doc:
                total_pages = len(doc)
                if total_pages == 0:
                    return {"success": False, "error": "PDF document contains zero pages", "pages": []}

                for page_num in range(total_pages):
                    page = doc[page_num]
                    text = page.get_text("text") or ""
                    # Simple heuristic: treat first line or bold block as section if available, else None
                    lines = [l.strip() for l in text.splitlines() if l.strip()]
                    section = lines[0] if lines and len(lines[0]) < 80 else None

                    pages.append(DocumentPage(
                        page_number=page_num + 1,
                        text=text,
                        section=section
                    ))

            return {
                "success": True,
                "file_name": os.path.basename(file_path),
                "total_pages": total_pages,
                "pages": pages,
                "error": None
            }
        except Exception as e:
            logger.error(f"PyMuPDF failed to parse PDF {file_path}: {e}")
            return {"success": False, "error": f"PDF parsing error: {e}", "pages": []}

    @classmethod
    def _load_text(cls, file_path: str) -> Dict[str, Any]:
        """Loads plain text or markdown documents, mapping them as a single page or multi-block."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            pages = [DocumentPage(page_number=1, text=content, section=None)]
            return {
                "success": True,
                "file_name": os.path.basename(file_path),
                "total_pages": 1,
                "pages": pages,
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to read text file {file_path}: {e}")
            return {"success": False, "error": f"Text reading error: {e}", "pages": []}

    @classmethod
    def _load_html(cls, file_path: str) -> Dict[str, Any]:
        """Loads HTML documents (basic text strip or future BeautifulSoup integration)."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Basic tag stripping fallback
            import re
            clean_text = re.sub(r"<[^>]+>", "", content)

            pages = [DocumentPage(page_number=1, text=clean_text, section=None)]
            return {
                "success": True,
                "file_name": os.path.basename(file_path),
                "total_pages": 1,
                "pages": pages,
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to read HTML file {file_path}: {e}")
            return {"success": False, "error": f"HTML reading error: {e}", "pages": []}
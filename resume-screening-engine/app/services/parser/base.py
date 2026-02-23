"""
Base Parser Contract

Defines the interface for all resume parser implementations.
This ensures that any parser (PyResParser, alternative implementations, etc.)
conforms to the same contract for consistency and testability.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ResumeParser(ABC):
    """
    Abstract base class defining the resume parser contract.

    All resume parser implementations must:
    1. Accept a file_path to the resume document
    2. Implement a parse() method that returns standardized extracted data
    3. Handle file validation and error cases appropriately
    """

    @abstractmethod
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse a resume file and extract structured data.

        Args:
            text: Optional text context (for forward compatibility)

        Returns:
            Dictionary containing extracted resume data with keys:
            - skills: List[str]
            - experience_years: int
            - education: List[str]
            - total_experience: int (for pyresparser compatibility)
            - name: str | None
            - email: str | None
            - mobile_number: str | None
            - college_name: str | None
            - degree: str | None
            - designation: str | None
            - company_names: List[str] | None
            - no_of_pages: int | None

        Raises:
            FileNotFoundError: If the resume file does not exist
            RuntimeError: If parsing fails due to library errors
            ValueError: If the file format is not supported
        """

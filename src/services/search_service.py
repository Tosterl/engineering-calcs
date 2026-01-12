"""
Search service for Engineering Calculations Database.

This module provides search functionality for finding formulas and calculations
using fuzzy matching and filtering by various criteria.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional, Type

from src.core.calculations import Calculation, calculation_registry


@dataclass
class SearchResult:
    """
    Container for a search result with relevance scoring.

    Attributes:
        calculation_class: The calculation class that matched the search.
        score: Relevance score between 0.0 and 1.0 (higher is better match).
        match_type: Type of match that triggered this result.
                   One of: 'name', 'description', 'category', 'variable'.
    """
    calculation_class: Type[Calculation]
    score: float
    match_type: str

    def __repr__(self) -> str:
        return (
            f"SearchResult("
            f"calculation={self.calculation_class.name!r}, "
            f"score={self.score:.3f}, "
            f"match_type={self.match_type!r})"
        )


class SearchService:
    """
    Service for searching calculations by various criteria.

    Provides fuzzy search by name, description, and category,
    as well as exact matching by variable names.

    Example:
        >>> service = SearchService()
        >>> results = service.search_calculations("stress")
        >>> for result in results:
        ...     print(f"{result.calculation_class.name}: {result.score:.2f}")
    """

    def __init__(self, min_score_threshold: float = 0.3) -> None:
        """
        Initialize the search service.

        Args:
            min_score_threshold: Minimum score for a result to be included.
                                Defaults to 0.3 (30% match).
        """
        self._min_score_threshold = min_score_threshold

    def _fuzzy_match(self, query: str, text: str) -> float:
        """
        Calculate fuzzy match score between query and text.

        Uses SequenceMatcher for similarity calculation with
        case-insensitive matching.

        Args:
            query: The search query string.
            text: The text to match against.

        Returns:
            Similarity score between 0.0 and 1.0.
        """
        if not query or not text:
            return 0.0

        query_lower = query.lower()
        text_lower = text.lower()

        # Exact substring match gets a bonus
        if query_lower in text_lower:
            # Bonus based on how much of the text the query covers
            base_score = len(query_lower) / len(text_lower)
            return min(1.0, 0.7 + (base_score * 0.3))

        # Use SequenceMatcher for fuzzy matching
        matcher = SequenceMatcher(None, query_lower, text_lower)
        return matcher.ratio()

    def _score_calculation(
        self,
        calc_class: Type[Calculation],
        query: str
    ) -> tuple[float, str]:
        """
        Score a calculation against a search query.

        Checks name, description, and category for matches.

        Args:
            calc_class: The calculation class to score.
            query: The search query.

        Returns:
            Tuple of (best_score, match_type).
        """
        scores = {
            'name': self._fuzzy_match(query, calc_class.name) * 1.2,  # Boost name matches
            'description': self._fuzzy_match(query, calc_class.description),
            'category': self._fuzzy_match(query, calc_class.category) * 1.1,  # Slight boost for category
        }

        # Find the best match type
        best_type = max(scores, key=scores.get)
        best_score = min(scores[best_type], 1.0)  # Cap at 1.0

        return best_score, best_type

    def search_calculations(
        self,
        query: str,
        category: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for calculations using fuzzy matching.

        Searches across calculation names, descriptions, and categories.
        Results are sorted by relevance score in descending order.

        Args:
            query: The search query string.
            category: Optional category to filter results. If provided,
                     only calculations in this category are searched.

        Returns:
            List of SearchResult objects sorted by score (highest first).

        Example:
            >>> service = SearchService()
            >>> results = service.search_calculations("beam deflection")
            >>> results = service.search_calculations("stress", category="Statics")
        """
        if not query:
            return []

        # Get calculations to search
        if category:
            calculations = calculation_registry.list_by_category(category)
        else:
            calculations = calculation_registry.list_all()

        results: List[SearchResult] = []

        for calc_class in calculations:
            score, match_type = self._score_calculation(calc_class, query)

            if score >= self._min_score_threshold:
                results.append(SearchResult(
                    calculation_class=calc_class,
                    score=score,
                    match_type=match_type
                ))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)

        return results

    def search_by_variable(self, variable_name: str) -> List[SearchResult]:
        """
        Find calculations that use a specific variable.

        Searches both input and output parameters for matching variable names.
        Uses fuzzy matching for flexibility.

        Args:
            variable_name: The variable name to search for.

        Returns:
            List of SearchResult objects sorted by score (highest first).

        Example:
            >>> service = SearchService()
            >>> results = service.search_by_variable("force")
            >>> for r in results:
            ...     print(f"{r.calculation_class.name} uses '{variable_name}'")
        """
        if not variable_name:
            return []

        results: List[SearchResult] = []
        calculations = calculation_registry.list_all()

        for calc_class in calculations:
            best_score = 0.0

            # Check input parameters
            for param in calc_class.input_params:
                score = self._fuzzy_match(variable_name, param.name)
                if score > best_score:
                    best_score = score

                # Also check parameter description
                desc_score = self._fuzzy_match(variable_name, param.description) * 0.8
                if desc_score > best_score:
                    best_score = desc_score

            # Check output parameters
            for param in calc_class.output_params:
                score = self._fuzzy_match(variable_name, param.name)
                if score > best_score:
                    best_score = score

                # Also check parameter description
                desc_score = self._fuzzy_match(variable_name, param.description) * 0.8
                if desc_score > best_score:
                    best_score = desc_score

            if best_score >= self._min_score_threshold:
                results.append(SearchResult(
                    calculation_class=calc_class,
                    score=best_score,
                    match_type='variable'
                ))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)

        return results

    def get_categories(self) -> List[str]:
        """
        Get all unique calculation categories.

        Returns:
            Sorted list of unique category names.

        Example:
            >>> service = SearchService()
            >>> categories = service.get_categories()
            >>> print(categories)
            ['Fluids', 'Materials', 'Statics', 'Thermodynamics']
        """
        return calculation_registry.get_categories()

    def get_calculations_by_category(
        self,
        category: str
    ) -> List[Type[Calculation]]:
        """
        Get all calculations in a specific category.

        Args:
            category: The category name to filter by.

        Returns:
            List of calculation classes in the specified category.

        Example:
            >>> service = SearchService()
            >>> statics_calcs = service.get_calculations_by_category("Statics")
            >>> for calc in statics_calcs:
            ...     print(calc.name)
        """
        return calculation_registry.list_by_category(category)


# Module exports
__all__ = [
    "SearchResult",
    "SearchService",
]

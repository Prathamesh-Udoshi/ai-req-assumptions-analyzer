"""
Scoring Module

This module provides scoring logic for requirements quality assessment.
Calculates ambiguity score, assumption score, and overall readiness score.
"""

from typing import Dict, Any, List, Tuple
from enum import Enum

from .ambiguity_detector import AmbiguityDetector, AmbiguityIssue
from .assumption_detector import AssumptionDetector, AssumptionIssue


class ReadinessLevel(Enum):
    """Classification levels for requirement readiness."""
    READY = "Ready"
    NEEDS_CLARIFICATION = "Needs clarification"
    HIGH_RISK = "High risk for automation"


class RequirementScorer:
    """
    Calculates quality scores for requirements and test cases.

    Provides three key metrics:
    - ambiguity_score: How ambiguous the text is (0-100)
    - assumption_score: How many hidden assumptions exist (0-100)
    - readiness_score: Overall readiness for automation (0-100)
    """

    def __init__(self):
        """Initialize the scorer with detector instances."""
        self.ambiguity_detector = AmbiguityDetector()
        self.assumption_detector = AssumptionDetector()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform complete multi-signal analysis of requirement text.

        Returns structured output with:
        - Multi-component ambiguity and assumption scores
        - Confidence indicators
        - Assumption strength classification
        - Impact explanations for each issue

        Args:
            text: Input requirement or test case text

        Returns:
            Dictionary with comprehensive analysis results
        """
        # Detect issues
        ambiguity_issues = self.ambiguity_detector.detect_ambiguities(text)
        assumption_issues = self.assumption_detector.detect_assumptions(text)

        # Calculate multi-signal scores
        ambiguity_analysis = self.ambiguity_detector.calculate_ambiguity_score(ambiguity_issues, text)
        assumption_analysis = self.assumption_detector.calculate_assumption_score(assumption_issues, text)

        # Calculate overall readiness
        readiness_score = self.calculate_readiness_score(
            ambiguity_analysis["score"],
            assumption_analysis["score"],
            text
        )
        readiness_level = self.classify_readiness(readiness_score)

        # Format issues with impact explanations
        issues = self._format_issues_with_impact(ambiguity_issues + assumption_issues)

        # Generate clarifying questions
        suggestions = self._generate_clarifying_questions(issues, text)

        return {
            "ambiguity": {
                "score": ambiguity_analysis["score"],
                "confidence": ambiguity_analysis["confidence"],
                "components": ambiguity_analysis["components"]
            },
            "assumptions": {
                "score": assumption_analysis["score"],
                "components": assumption_analysis["components"]
            },
            "readiness_score": round(readiness_score, 1),
            "readiness_level": readiness_level.value,
            "issues": issues,
            "clarifying_questions": suggestions
        }

    def calculate_readiness_score(self, ambiguity_score: float, assumption_score: float, text: str = "") -> float:
        """
        Enhanced readiness calculation with context-aware weighting.

        Key improvements:
        - Assumption-weighted scoring (assumptions are more critical for test automation)
        - Severity-based weighting within each category
        - Text complexity consideration
        - Non-linear scoring curve

        Args:
            ambiguity_score: Score from ambiguity detection (0-100)
            assumption_score: Score from assumption detection (0-100)
            text: Original text for context analysis

        Returns:
            Readiness score from 0-100 (higher = more ready)
        """
        # More sensitive weighting for better calibration
        if assumption_score > ambiguity_score:
            # When assumptions dominate, they're much more critical
            assumption_weight = 0.8
            ambiguity_weight = 0.2
        elif ambiguity_score > 60:
            # High ambiguity needs significant attention
            ambiguity_weight = 0.7
            assumption_weight = 0.3
        else:
            # Balanced case but still favor assumptions
            ambiguity_weight = 0.4
            assumption_weight = 0.6

        # Stronger severity multipliers for better differentiation
        if assumption_score > 70:
            assumption_weight *= 1.5  # Critical assumptions heavily weighted
        if ambiguity_score > 70:
            ambiguity_weight *= 1.3  # Critical ambiguity also weighted

        # Text complexity adjustment
        text_length = len(text.split()) if text else 50
        complexity_factor = 1.0
        if text_length < 10:
            complexity_factor = 1.2  # Very short texts are more critical
        elif text_length > 100:
            complexity_factor = 0.9  # Very long texts can be more forgiving

        # Calculate weighted impact with bounded non-linear scaling
        ambiguity_impact = min(80, (ambiguity_score ** 0.8)) * ambiguity_weight  # Bound and scale
        assumption_impact = min(85, (assumption_score ** 0.9)) * assumption_weight  # Bound and scale

        total_impact = ambiguity_impact + assumption_impact

        # Readiness score with improved sigmoid-like normalization
        # Much more sensitive to issues for better calibration
        readiness = 100 / (1 + total_impact / 10)  # Very sensitive inflection point

        # Apply complexity adjustment with bounds
        readiness = readiness * complexity_factor

        # Additional safeguard against extreme scores
        if total_impact > 120:  # Very high combined impact
            readiness = max(readiness * 0.8, 10)  # Minimum readiness of 10
        elif total_impact > 100:  # High combined impact
            readiness = max(readiness * 0.9, 15)  # Minimum readiness of 15

        return max(0.0, min(95.0, readiness))  # Allow very low scores for poor requirements

    def classify_readiness(self, readiness_score: float) -> ReadinessLevel:
        """
        Classify readiness level based on score.

        Args:
            readiness_score: Calculated readiness score (0-100)

        Returns:
            ReadinessLevel enum value
        """
        if readiness_score >= 70:
            return ReadinessLevel.READY
        elif readiness_score >= 40:
            return ReadinessLevel.NEEDS_CLARIFICATION
        else:
            return ReadinessLevel.HIGH_RISK

    def _format_issues(self, issues: List) -> List[Dict[str, Any]]:
        """
        Convert issue objects to serializable dictionaries.

        Args:
            issues: List of AmbiguityIssue and AssumptionIssue objects

        Returns:
            List of dictionaries with issue details
        """
        formatted_issues = []

        for issue in issues:
            if hasattr(issue, 'category'):  # AssumptionIssue
                formatted_issues.append({
                    "type": issue.type,
                    "category": issue.category,
                    "text": issue.text,
                    "message": issue.message,
                    "assumption": issue.assumption
                })
            else:  # AmbiguityIssue
                formatted_issues.append({
                    "type": issue.type,
                    "text": issue.text,
                    "message": issue.message,
                    "start_char": issue.start_char,
                    "end_char": issue.end_char
                })

        return formatted_issues

    def _format_issues_with_impact(self, issues: List) -> List[Dict[str, Any]]:
        """
        Convert issues to serializable format with impact explanations.

        Each issue includes:
        - Type and message
        - Why this matters for testing/automation
        - What could go wrong if left unclear
        """
        formatted_issues = []

        for issue in issues:
            if hasattr(issue, 'category'):  # AssumptionIssue
                formatted_issue = {
                    "type": "Assumption",
                    "message": issue.message,
                    "category": issue.category,
                    "assumption": issue.assumption,
                    "impact": self._get_assumption_impact(issue)
                }
            else:  # AmbiguityIssue
                formatted_issue = {
                    "type": "Ambiguity",
                    "message": issue.message,
                    "impact": self._get_ambiguity_impact(issue)
                }
            formatted_issues.append(formatted_issue)

        return formatted_issues

    def _get_ambiguity_impact(self, issue) -> str:
        """Generate impact explanation for ambiguity issues."""
        issue_type = issue.type
        issue_text = issue.text.lower()

        impact_map = {
            "Subjective term": {
                "fast": "May cause inconsistent test expectations and flaky performance tests",
                "slow": "May lead to unclear acceptance criteria for response times",
                "secure": "May result in inadequate security testing coverage",
                "user-friendly": "May cause subjective interpretation of usability requirements",
                "reliable": "May lead to undefined reliability and stability expectations",
                "scalable": "May result in unclear performance scaling requirements",
                "optimal": "May cause ambiguous optimization goals and success criteria",
                "default": "May lead to subjective interpretation and inconsistent testing"
            },
            "Weak modality": {
                "should": "Creates uncertainty about whether this is a requirement or suggestion",
                "could": "May result in optional implementation and inconsistent behavior",
                "might": "Creates ambiguity about expected behavior under different conditions",
                "may": "May lead to inconsistent implementation across different scenarios",
                "default": "Creates uncertainty about requirement priority and implementation"
            },
            "Undefined reference": "May cause confusion about what specific element or condition is being referenced",
            "Non-testable statement": "Makes it impossible to create objective test cases and acceptance criteria"
        }

        if issue_type in impact_map:
            if isinstance(impact_map[issue_type], dict):
                return impact_map[issue_type].get(issue_text, impact_map[issue_type].get("default", "May cause testing ambiguity"))
            else:
                return impact_map[issue_type]

        return "May lead to unclear requirements and inconsistent testing"

    def _get_assumption_impact(self, issue) -> str:
        """Generate impact explanation for assumption issues."""
        assumption_text = issue.assumption.lower()
        category = issue.category

        # Critical assumptions that break automation
        critical_patterns = [
            "user exists", "credentials exist", "user logged in", "permissions granted",
            "browser", "database", "api", "server", "environment"
        ]

        for pattern in critical_patterns:
            if pattern in assumption_text:
                return f"Critical assumption - missing {pattern.replace('_', ' ')} will cause test automation to fail"

        # Moderate assumptions
        if "data" in assumption_text or "record" in assumption_text:
            return "May cause test data setup issues and inconsistent test results"

        if "configuration" in assumption_text or "setup" in assumption_text:
            return "May lead to environment-specific test failures and deployment issues"

        # Default impact based on category
        category_impacts = {
            "Environment": "May cause test failures in different environments or platforms",
            "State": "May lead to flaky tests due to unpredictable system state",
            "Data": "May result in test data inconsistencies and unreliable test execution"
        }

        return category_impacts.get(category, "May lead to unexpected test behavior and automation failures")

    def _generate_clarifying_questions(self, issues: List[Dict], text: str) -> List[str]:
        """Generate clarifying questions based on detected issues."""
        questions = []

        # Always include some standard questions for comprehensive coverage
        questions.extend([
            "What are the exact preconditions required for this test?",
            "What is the expected result and how should it be verified?"
        ])

        # Add issue-specific questions
        for issue in issues:
            if issue["type"] == "Ambiguity":
                question = self._get_ambiguity_question(issue)
                if question and question not in questions:
                    questions.append(question)
            elif issue["type"] == "Assumption":
                question = self._get_assumption_question(issue)
                if question and question not in questions:
                    questions.append(question)

        return questions[:8]  # Limit to 8 questions to avoid overwhelming

    def _get_ambiguity_question(self, issue: Dict) -> str:
        """Generate clarifying question for ambiguity issue."""
        message = issue["message"].lower()

        question_map = {
            "subjective term": "What specific, measurable criteria define success for this requirement?",
            "weak modality": "Is this a mandatory requirement or optional behavior?",
            "undefined reference": "What specific element or condition does this refer to?",
            "non-testable": "What specific, observable behavior would indicate success?"
        }

        for key, question in question_map.items():
            if key in message:
                return question

        return "What specific criteria should be used to evaluate this requirement?"

    def _get_assumption_question(self, issue: Dict) -> str:
        """Generate clarifying question for assumption issue."""
        assumption = issue.get("assumption", "").lower()

        question_map = {
            "user exists": "What test user accounts should be prepared?",
            "credentials": "What user credentials are needed for testing?",
            "logged in": "Should the user be pre-authenticated for this test?",
            "permissions": "What user roles and permissions are required?",
            "browser": "Which browsers and versions should be supported?",
            "database": "What database state should exist before testing?",
            "environment": "What environmental conditions are required?",
            "data": "What test data should be prepared?"
        }

        for key, question in question_map.items():
            if key in assumption:
                return question

        return "What specific conditions or data are required for this test?"

    def classify_test_case_type(self, text: str) -> str:
        """Classify test case type to adjust scoring weights."""
        text_lower = text.lower()

        if any(word in text_lower for word in ['login', 'authenticate', 'sign in']):
            return 'authentication'
        elif any(word in text_lower for word in ['search', 'filter', 'find', 'query']):
            return 'data_retrieval'
        elif any(word in text_lower for word in ['create', 'add', 'insert', 'submit']):
            return 'data_creation'
        elif any(word in text_lower for word in ['update', 'edit', 'modify', 'change']):
            return 'data_modification'
        elif any(word in text_lower for word in ['delete', 'remove', 'archive']):
            return 'data_deletion'
        elif any(word in text_lower for word in ['api', 'endpoint', 'request', 'response']):
            return 'api_testing'
        elif any(word in text_lower for word in ['ui', 'interface', 'screen', 'page']):
            return 'ui_testing'
        else:
            return 'general'


# Test case type-specific weights
TEST_CASE_TYPE_WEIGHTS = {
    'authentication': {'ambiguity_weight': 0.4, 'assumption_weight': 0.6},  # Auth assumptions more critical
    'api_testing': {'ambiguity_weight': 0.5, 'assumption_weight': 0.5},     # Balanced for APIs
    'ui_testing': {'ambiguity_weight': 0.6, 'assumption_weight': 0.4},      # UI ambiguity more critical
    'data_creation': {'ambiguity_weight': 0.4, 'assumption_weight': 0.6},   # Data assumptions critical
    'data_modification': {'ambiguity_weight': 0.45, 'assumption_weight': 0.55}, # Balanced
    'data_deletion': {'ambiguity_weight': 0.35, 'assumption_weight': 0.65}, # Deletion assumptions most critical
    'data_retrieval': {'ambiguity_weight': 0.5, 'assumption_weight': 0.5},  # Balanced
    'general': {'ambiguity_weight': 0.45, 'assumption_weight': 0.55}        # Default balanced
}


class OptimizedRequirementScorer(RequirementScorer):
    """Optimized scorer with caching for better performance."""

    def __init__(self):
        super().__init__()
        import time
        self.score_cache = {}  # Cache for repeated similar texts
        self.time = time

    def analyze_text_with_caching(self, text: str) -> Dict[str, Any]:
        """Analyze with intelligent caching for performance."""
        text_hash = hash(text.lower().strip())

        if text_hash in self.score_cache:
            cached_result = self.score_cache[text_hash]
            # Check if cache is still valid (simple TTL)
            if self.time.time() - cached_result.get('timestamp', 0) < 3600:  # 1 hour TTL
                return cached_result['result']

        # Perform full analysis
        result = self.analyze_text(text)

        # Cache result
        self.score_cache[text_hash] = {
            'result': result,
            'timestamp': self.time.time()
        }

        # Limit cache size
        if len(self.score_cache) > 1000:
            oldest_key = min(self.score_cache.keys(),
                           key=lambda k: self.score_cache[k]['timestamp'])
            del self.score_cache[oldest_key]

        return result

    def get_score_breakdown(self, text: str) -> Dict[str, Any]:
        """
        Get detailed score breakdown for debugging/analysis.

        Args:
            text: Input requirement or test case text

        Returns:
            Detailed breakdown of scoring components
        """
        ambiguity_issues = self.ambiguity_detector.detect_ambiguities(text)
        assumption_issues = self.assumption_detector.detect_assumptions(text)

        ambiguity_score = self.ambiguity_detector.calculate_ambiguity_score(ambiguity_issues)
        assumption_score = self.assumption_detector.calculate_assumption_score(assumption_issues)
        readiness_score = self.calculate_readiness_score(ambiguity_score, assumption_score)

        return {
            "text": text,
            "ambiguity": {
                "score": round(ambiguity_score, 1),
                "issue_count": len(ambiguity_issues),
                "issues": [issue.type for issue in ambiguity_issues]
            },
            "assumptions": {
                "score": round(assumption_score, 1),
                "issue_count": len(assumption_issues),
                "categories": list(set(issue.category for issue in assumption_issues if hasattr(issue, 'category')))
            },
            "readiness": {
                "score": round(readiness_score, 1),
                "level": self.classify_readiness(readiness_score).value,
                "formula": f"100 - ({ambiguity_score:.1f} * 0.5 + {assumption_score:.1f} * 0.5)"
            }
        }
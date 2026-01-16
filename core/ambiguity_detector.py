"""
Ambiguity Detection Module

This module provides rule-based detection of ambiguity in requirements and test cases.
Uses spaCy for tokenization, POS tagging, and dependency parsing to identify:
- Subjective/vague terms
- Weak modality terms
- Undefined references
- Non-testable statements
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

import spacy
from spacy.tokens import Doc


@dataclass
class AmbiguityIssue:
    """Represents a detected ambiguity issue."""
    type: str
    text: str
    message: str
    start_char: int = None
    end_char: int = None


# Calibrated ambiguity weights (reduced for better score distribution)
AMBIGUITY_WEIGHTS = {
    "Subjective term": {
        "performance": 6,     # Fast, slow, quick - impacts timing tests
        "quality": 5,         # Good, bad - moderate impact
        "usability": 8,       # Easy, hard - affects user experience tests
        "reliability": 8,     # Reliable, robust - important for stability tests
        "security": 9,        # Secure, safe - high priority for security tests
        "scalability": 7,     # Scalable - important for load tests
        "efficiency": 6,      # Efficient - affects resource usage tests
        "accuracy": 10,       # Accurate, precise - important for data validation
        "compatibility": 7,   # Compatible - affects integration tests
        "maintainability": 6  # Maintainable - affects long-term test maintenance
    },
    "Weak modality": {
        "possibility": 5,     # May, might, could - moderate uncertainty
        "preference": 6,      # Should, preferably - higher uncertainty
        "conditionality": 7,  # If possible, depending on - high uncertainty
        "frequency": 4,       # Sometimes, usually - lower uncertainty
        "probability": 6,     # Probably, likely - high uncertainty
        "tentativeness": 5    # Perhaps, maybe - moderate uncertainty
    },
    "Undefined reference": 9,   # Critical - causes test failures
    "Non-testable statement": 15 # Most critical - makes testing impossible
}


class AmbiguityDetector:
    """
    Detects various types of ambiguity in requirement text using rule-based NLP.

    This detector identifies:
    - Subjective terms (fast, secure, scalable, etc.)
    - Weak modality (should, could, might, etc.)
    - Undefined references (it, this, that without clear antecedent)
    - Non-testable statements (handle properly, work correctly)
    """

    def __init__(self, nlp_model: str = "en_core_web_sm"):
        """
        Initialize the ambiguity detector.

        Args:
            nlp_model: spaCy language model to use (default: en_core_web_sm)
        """
        try:
            self.nlp = spacy.load(nlp_model)
        except OSError:
            # Fallback to blank model if en_core_web_sm not available
            self.nlp = spacy.blank("en")

        # Define ambiguity patterns
        self.subjective_terms = {
            "fast", "slow", "quick", "rapid", "secure", "safe", "scalable",
            "optimal", "efficient", "user-friendly", "intuitive", "robust",
            "reliable", "stable", "flexible", "portable", "compatible",
            "accessible", "responsive", "smooth", "seamless", "clean",
            "proper", "correct", "appropriate", "adequate", "sufficient"
        }

        self.weak_modality_terms = {
            "should", "could", "might", "may", "can", "if possible",
            "as needed", "when necessary", "ideally", "preferably"
        }

        self.undefined_references = {
            "it", "this", "that", "these", "those", "the system",
            "the component", "the application", "the user"
        }

        self.non_testable_patterns = [
            r"handle.*properly",
            r"work.*correctly",
            r"function.*properly",
            r"behave.*correctly",
            r"perform.*properly",
            r"process.*correctly"
        ]

    def detect_ambiguities(self, text: str) -> List[AmbiguityIssue]:
        """
        Detect all types of ambiguity in the given text.

        Args:
            text: Input requirement or test case text

        Returns:
            List of AmbiguityIssue objects with detected problems
        """
        issues = []

        # Process text with spaCy
        doc = self.nlp(text.lower())

        # Detect subjective terms
        issues.extend(self._detect_subjective_terms(doc, text))

        # Detect weak modality
        issues.extend(self._detect_weak_modality(doc, text))

        # Detect undefined references
        issues.extend(self._detect_undefined_references(doc, text))

        # Detect non-testable statements
        issues.extend(self._detect_non_testable_statements(text))

        return issues

    def _detect_subjective_terms(self, doc: Doc, original_text: str) -> List[AmbiguityIssue]:
        """
        Detect subjective terms with context-aware logic.

        Only flags terms that lack quantitative context or specific constraints.
        """
        issues = []

        for token in doc:
            token_text = token.text.lower()
            if token_text in self.subjective_terms:
                # Context-aware checking: don't flag if quantitative/security/usability context exists
                should_flag = True

                if token_text == "fast":
                    should_flag = not self._has_performance_context(token, doc, original_text)
                elif token_text in ["secure", "safe"]:
                    should_flag = not self._has_security_context(token, doc, original_text)
                elif token_text == "user-friendly":
                    should_flag = not self._has_usability_context(token, doc, original_text)
                elif token_text == "reliable":
                    should_flag = not self._has_reliability_context(token, doc, original_text)
                elif token_text == "scalable":
                    should_flag = not self._has_scalability_context(token, doc, original_text)
                else:
                    # For other subjective terms, check for any quantitative context
                    should_flag = not self._has_quantitative_context(token, doc, original_text)

                if should_flag:
                    start_char = self._find_char_position(original_text, token.text, token.idx)
                    end_char = start_char + len(token.text) if start_char is not None else None

                    issues.append(AmbiguityIssue(
                        type="Subjective term",
                        text=token.text,
                        message=f"Subjective term '{token.text}' lacks specific, measurable criteria",
                        start_char=start_char,
                        end_char=end_char
                    ))

        return issues

    def _detect_weak_modality(self, doc: Doc, original_text: str) -> List[AmbiguityIssue]:
        """Detect weak modality terms that indicate optionality."""
        issues = []

        for token in doc:
            if token.text in self.weak_modality_terms:
                start_char = self._find_char_position(original_text, token.text, token.idx)
                end_char = start_char + len(token.text) if start_char is not None else None

                issues.append(AmbiguityIssue(
                    type="Weak modality",
                    text=token.text,
                    message=f"Optional/weak requirement term: '{token.text}'",
                    start_char=start_char,
                    end_char=end_char
                ))

        return issues

    def _detect_undefined_references(self, doc: Doc, original_text: str) -> List[AmbiguityIssue]:
        """Detect pronouns and references without clear antecedents."""
        issues = []

        for token in doc:
            if token.text in self.undefined_references:
                # Check if this is likely an undefined reference
                # Simple heuristic: if it's a pronoun or demonstrative without clear context
                if self._is_undefined_reference(token, doc):
                    start_char = self._find_char_position(original_text, token.text, token.idx)
                    end_char = start_char + len(token.text) if start_char is not None else None

                    issues.append(AmbiguityIssue(
                        type="Undefined reference",
                        text=token.text,
                        message=f"Potentially undefined reference: '{token.text}'",
                        start_char=start_char,
                        end_char=end_char
                    ))

        return issues

    def _detect_non_testable_statements(self, text: str) -> List[AmbiguityIssue]:
        """Detect statements that are too vague to be testable."""
        issues = []

        text_lower = text.lower()
        for pattern in self.non_testable_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                issues.append(AmbiguityIssue(
                    type="Non-testable statement",
                    text=match.group(),
                    message=f"Non-testable requirement: '{match.group()}'",
                    start_char=match.start(),
                    end_char=match.end()
                ))

        return issues

    def _is_undefined_reference(self, token, doc: Doc) -> bool:
        """
        Determine if a token is likely an undefined reference.

        This is a simple heuristic - in production, this could be enhanced
        with more sophisticated coreference resolution.
        """
        # Simple heuristics for undefined references
        if token.pos_ == "PRON" or token.dep_ in ["det", "poss"]:
            # Check if there's a clear antecedent in nearby context
            # This is a simplified approach - real coreference resolution is complex
            return True

        return False

    def _find_char_position(self, original_text: str, token_text: str, token_idx: int) -> int:
        """
        Find the character position of a token in the original text.

        This is a simplified approach. In production, spaCy's character offsets
        should be used if available.
        """
        try:
            # Simple approach: find the token in the original text
            # This may not be perfect for complex texts
            return original_text.lower().find(token_text, token_idx)
        except:
            return None

    def calculate_ambiguity_score(self, issues: List[AmbiguityIssue], text: str = "") -> Dict[str, Any]:
        """
        Calculate multi-signal ambiguity score with component breakdown.

        Returns detailed scoring with three components:
        - lexical_ambiguity_score: subjective/vague terms
        - testability_gap_score: non-testable statements
        - reference_uncertainty_score: undefined pronouns/entities

        Args:
            issues: List of detected ambiguity issues
            text: Original text for context analysis

        Returns:
            Dictionary with overall score and component scores
        """
        if not issues:
            return {
                "score": 0.0,
                "confidence": "HIGH",
                "components": {
                    "lexical": 0.0,
                    "testability": 0.0,
                    "references": 0.0
                }
            }

        # Categorize issues by type
        lexical_issues = []
        testability_issues = []
        reference_issues = []

        for issue in issues:
            if issue.type == "Subjective term":
                lexical_issues.append(issue)
            elif issue.type == "Non-testable statement":
                testability_issues.append(issue)
            elif issue.type == "Undefined reference":
                reference_issues.append(issue)
            elif issue.type == "Weak modality":
                # Weak modality contributes to both lexical and testability
                lexical_issues.append(issue)
                testability_issues.append(issue)

        # Calculate component scores
        lexical_score = self._calculate_component_score(lexical_issues, text, "lexical")
        testability_score = self._calculate_component_score(testability_issues, text, "testability")
        reference_score = self._calculate_component_score(reference_issues, text, "references")

        # Overall score: weighted average with testability most important
        overall_score = (lexical_score * 0.3 + testability_score * 0.5 + reference_score * 0.2)

        # Calculate confidence based on text length and issue diversity
        confidence = self._calculate_confidence(text, issues)

        return {
            "score": round(overall_score, 1),
            "confidence": confidence,
            "components": {
                "lexical": round(lexical_score, 1),
                "testability": round(testability_score, 1),
                "references": round(reference_score, 1)
            }
        }

        # Count issues by type to handle multiples
        issue_counts = {}
        for issue in issues:
            issue_type = issue.type
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Calculate base score from issue types with enhanced weights
        base_score = 0
        for issue in issues:
            issue_type = issue.type
            if issue_type in base_weights:
                if isinstance(base_weights[issue_type], dict):
                    # Handle nested weights (e.g., subjective terms by category)
                    weight = self._get_subjective_term_weight(issue, base_weights[issue_type])
                else:
                    # Direct weight for simple types
                    weight = base_weights[issue_type]
                base_score += weight
            else:
                base_score += 6  # Default weight

        # Apply diminishing returns for multiple issues
        issue_count = len(issues)
        if issue_count > 1:
            # Bonus for multiple different types of issues
            type_diversity_bonus = len(issue_counts) * 2
            base_score += min(10, type_diversity_bonus)

        # Factor in text length and density
        text_length = len(text.split()) if text else 50  # Default to 50 words if not provided

        # Improved density calculation with logarithmic scaling
        density_factor = len(issues) / max(text_length, 5)  # More reasonable minimum

        # Complexity factor based on text length (less aggressive)
        if text_length < 8:
            complexity_factor = 1.1  # Very short texts slightly more critical
        elif text_length < 25:
            complexity_factor = 1.0  # Normal texts
        else:
            complexity_factor = 0.9  # Long texts slightly more forgiving

        # Calculate density score with logarithmic scaling to prevent extremes
        if density_factor <= 0.1:
            density_score = density_factor * 50  # Low density: linear scaling
        elif density_factor <= 0.5:
            density_score = 5 + (density_factor - 0.1) * 60  # Medium density: moderate scaling
        else:
            density_score = 35 + min(25, (density_factor - 0.5) * 40)  # High density: capped growth

        # Calculate final score with better bounds
        raw_score = (base_score * complexity_factor) + density_score

        # Improved sigmoid normalization with better extreme handling
        if raw_score <= 10:
            final_score = raw_score * 0.7  # Very low scores reduced more
        elif raw_score <= 30:
            final_score = raw_score * 0.85  # Low scores slightly reduced
        elif raw_score <= 70:
            final_score = raw_score  # Middle range unchanged
        elif raw_score <= 90:
            final_score = 70 + (raw_score - 70) * 0.6  # High scores moderately dampened
        else:
            final_score = 82 + (raw_score - 90) * 0.2  # Very high scores heavily dampened

        return max(0.0, min(100.0, final_score))

    def _calculate_component_score(self, component_issues: List[AmbiguityIssue], text: str, component_type: str) -> float:
        """Calculate score for a specific ambiguity component."""
        if not component_issues:
            return 0.0

        base_weights = AMBIGUITY_WEIGHTS
        base_score = 0

        for issue in component_issues:
            issue_type = issue.type
            if issue_type in base_weights:
                if isinstance(base_weights[issue_type], dict):
                    weight = self._get_subjective_term_weight(issue, base_weights[issue_type])
                else:
                    weight = base_weights[issue_type]
                base_score += weight

        # Component-specific density calculation
        text_length = len(text.split()) if text else 50
        density_factor = len(component_issues) / max(text_length, 5)

        # Different scaling for different components
        if component_type == "lexical":
            density_score = min(30, density_factor * 60)
        elif component_type == "testability":
            density_score = min(40, density_factor * 80)  # Testability is more critical
        else:  # references
            density_score = min(35, density_factor * 70)

        raw_score = base_score + density_score

        # Conservative normalization
        if raw_score > 80:
            return 80 + (raw_score - 80) * 0.3
        return min(100.0, raw_score)

    def _calculate_confidence(self, text: str, issues: List[AmbiguityIssue]) -> str:
        """Calculate confidence level for ambiguity analysis."""
        text_length = len(text.split())
        issue_count = len(issues)
        issue_types = len(set(issue.type for issue in issues))

        # High confidence: sufficient text length, multiple issue types, reasonable issue density
        if text_length >= 10 and issue_types >= 2 and (issue_count / max(text_length, 1)) <= 0.5:
            return "HIGH"
        # Medium confidence: adequate text but limited signals
        elif text_length >= 5 and issue_count > 0:
            return "MEDIUM"
        # Low confidence: very short text or no clear signals
        else:
            return "LOW"

    def _get_subjective_term_weight(self, issue: AmbiguityIssue, category_weights: dict) -> float:
        """Get weight for subjective terms based on their category."""
        if issue.type != "Subjective term":
            return 8  # Default for subjective terms

        issue_text = issue.text.lower()

        # Map subjective terms to categories
        category_mapping = {
            "performance": ["fast", "slow", "quick", "rapid", "speedy", "swift", "brisk",
                          "sluggish", "laggy", "smooth", "responsive", "snappy", "nimble",
                          "agile", "zippy", "crawling", "glacial", "lethargic", "tardy",
                          "delayed", "unresponsive", "clunky", "fluid", "seamless", "effortless",
                          "lightning", "blazing", "superfast", "ultrafast"],
            "quality": ["good", "bad", "better", "best", "worse", "worst", "excellent",
                       "poor", "superior", "inferior", "great", "terrible", "superb", "awful",
                       "outstanding", "mediocre", "exceptional", "subpar", "premium",
                       "low-quality", "high-quality", "top-notch", "first-rate", "second-rate",
                       "world-class", "substandard", "impressive", "dismal", "stellar",
                       "pathetic", "magnificent", "shoddy", "splendid", "lousy"],
            "usability": ["easy", "hard", "simple", "complex", "intuitive", "confusing",
                         "user-friendly", "difficult", "straightforward", "complicated",
                         "accessible", "inaccessible", "ergonomic", "awkward", "natural",
                         "unnatural", "obvious", "non-obvious", "self-explanatory", "puzzling",
                         "clear", "unclear", "transparent", "opaque", "learnable", "steep",
                         "gentle", "frustrating", "pleasing", "annoying"],
            "reliability": ["reliable", "unreliable", "robust", "fragile", "stable", "unstable",
                           "consistent", "inconsistent", "dependable", "flaky", "trustworthy",
                           "untrustworthy", "solid", "breakable", "steady", "erratic",
                           "predictable", "unpredictable", "bulletproof", "vulnerable",
                           "resilient", "brittle", "fault-tolerant", "failure-prone"],
            "security": ["secure", "insecure", "safe", "unsafe", "protected", "vulnerable",
                        "trustworthy", "risky", "encrypted", "exposed", "guarded", "defenseless",
                        "fortified", "weak", "tamper-proof", "hackable", "authenticated",
                        "unauthenticated", "authorized", "unauthorized", "validated",
                        "unvalidated", "sanitized", "contaminated"],
            "scalability": ["scalable", "non-scalable", "flexible", "rigid", "adaptable",
                           "inflexible", "extensible", "limited", "expandable", "constrained",
                           "elastic", "static", "dynamic", "fixed", "modular", "monolithic",
                           "distributed", "centralized", "cloud-ready", "on-premise",
                           "horizontal", "vertical", "auto-scaling", "manual"],
            "efficiency": ["efficient", "inefficient", "optimal", "suboptimal", "effective",
                          "ineffective", "productive", "wasteful", "streamlined", "cumbersome",
                          "lean", "bloated", "concise", "verbose", "succinct", "redundant",
                          "economical", "extravagant", "frugal", "lavish", "thrifty", "wasteful",
                          "resourceful", "profligate"],
            "accuracy": ["accurate", "inaccurate", "precise", "imprecise", "exact", "inexact",
                        "correct", "incorrect", "right", "wrong", "valid", "invalid", "true",
                        "false", "factual", "erroneous", "authentic", "fake", "genuine",
                        "counterfeit", "legitimate", "bogus"],
            "compatibility": ["compatible", "incompatible", "interoperable", "non-interoperable",
                             "universal", "proprietary", "standard", "custom", "open", "closed",
                             "cross-platform", "platform-specific", "vendor-neutral",
                             "vendor-locked", "agnostic", "dependent"],
            "maintainability": ["maintainable", "unmaintainable", "modular", "monolithic",
                               "clean", "messy", "readable", "unreadable", "organized",
                               "disorganized", "structured", "chaotic", "documented",
                               "undocumented", "testable", "untestable", "debuggable", "opaque"]
        }

        # Find which category this term belongs to
        for category, terms in category_mapping.items():
            if issue_text in terms:
                return category_weights.get(category, 8)

        return category_weights.get("quality", 8)  # Default to quality category

    def _has_quantitative_context(self, token, doc: Doc, text: str) -> bool:
        """Check if a subjective term has quantitative context (numbers, units, etc.)."""
        # Look for numbers, units, percentages within reasonable distance
        token_start = token.idx
        token_end = token_start + len(token.text)

        # Search in a window around the token (±50 characters)
        search_start = max(0, token_start - 50)
        search_end = min(len(text), token_end + 50)
        context_window = text[search_start:search_end].lower()

        # Check for quantitative indicators
        quantitative_patterns = [
            r'\d+',  # numbers
            r'\d+\s*(?:ms|sec|second|minute|hour|day)',  # time units
            r'\d+\s*(?:%|percent)',  # percentages
            r'\d+\s*(?:px|pixel|mb|gb|kb)',  # size units
            r'\d+\s*(?:user|request|transaction|operation)',  # countable units
            r'less than|greater than|at least|at most',  # comparative quantifiers
            r'\d+\.\d+',  # decimals
            r'zero|one|two|three|four|five|six|seven|eight|nine|ten'  # written numbers
        ]

        for pattern in quantitative_patterns:
            if re.search(pattern, context_window, re.IGNORECASE):
                return True

        return False

    def _has_performance_context(self, token, doc: Doc, text: str) -> bool:
        """Check if 'fast' or performance terms have specific timing context."""
        context_window = self._get_context_window(token, text, 100)
        context_lower = context_window.lower()

        # Check for timing specifications
        timing_patterns = [
            r'\d+\s*(?:ms|millisecond|sec|second|minute)',  # explicit times
            r'under|within|less than|no more than',  # timing constraints
            r'response time|load time|render time',  # performance metrics
            r'\d+\s*fps|frames per second',  # frame rates
            r'latency|throughput|bandwidth'  # performance terms
        ]

        for pattern in timing_patterns:
            if re.search(pattern, context_lower):
                return True

        return False

    def _has_security_context(self, token, doc: Doc, text: str) -> bool:
        """Check if security terms have specific security mechanisms mentioned."""
        context_window = self._get_context_window(token, text, 150)
        context_lower = context_window.lower()

        # Check for security mechanisms
        security_patterns = [
            r'encryption|ssl|tls|https|oauth|jwt|saml',  # protocols
            r'authentication|authorization|auth',  # auth methods
            r'firewall|vpn|certificate|key',  # security tech
            r'sql injection|xss|csrf|attack|threat',  # security concerns
            r'password|credential|token|session',  # auth elements
            r'aes|rsa|sha|hash|salt'  # crypto algorithms
        ]

        for pattern in security_patterns:
            if re.search(pattern, context_lower):
                return True

        return False

    def _has_usability_context(self, token, doc: Doc, text: str) -> bool:
        """Check if usability terms have specific usability criteria."""
        context_window = self._get_context_window(token, text, 100)
        context_lower = context_window.lower()

        # Check for usability metrics or specific criteria
        usability_patterns = [
            r'accessibility|wcag|contrast|font size',  # accessibility
            r'click|tap|gesture|navigation|menu',  # interaction patterns
            r'error message|feedback|guidance',  # user feedback
            r'learning curve|training time',  # learnability metrics
            r'efficiency|effectiveness|satisfaction',  # usability factors
            r'task completion|success rate|error rate'  # measurable usability
        ]

        for pattern in usability_patterns:
            if re.search(pattern, context_lower):
                return True

        return False

    def _has_reliability_context(self, token, doc: Doc, text: str) -> bool:
        """Check if reliability terms have specific reliability metrics."""
        context_window = self._get_context_window(token, text, 100)
        context_lower = context_window.lower()

        # Check for reliability metrics
        reliability_patterns = [
            r'\d+\s*(?:%|percent)\s*uptime',  # uptime percentages
            r'mean time|mtbf|mttr',  # reliability metrics
            r'availability|sla|downtime',  # service level terms
            r'redundancy|failover|backup',  # reliability mechanisms
            r'error rate|failure rate|recovery',  # failure metrics
            r'\d+\s*nines|five nines|four nines'  # uptime specifications
        ]

        for pattern in reliability_patterns:
            if re.search(pattern, context_lower):
                return True

        return False

    def _has_scalability_context(self, token, doc: Doc, text: str) -> bool:
        """Check if scalability terms have specific scaling criteria."""
        context_window = self._get_context_window(token, text, 100)
        context_lower = context_window.lower()

        # Check for scalability metrics
        scalability_patterns = [
            r'\d+\s*(?:user|request|transaction|connection)',  # load specifications
            r'concurrent|simultaneous|parallel',  # concurrency indicators
            r'horizontal|vertical|auto.?scal',  # scaling types
            r'load balanc|cluster|distributed',  # scaling architecture
            r'peak|maximum|capacity|throughput',  # capacity terms
            r'elastic|dynamic|on.?demand'  # elastic scaling
        ]

        for pattern in scalability_patterns:
            if re.search(pattern, context_lower):
                return True

        return False

    def _get_context_window(self, token, text: str, window_size: int = 100) -> str:
        """Get text window around a token for context analysis."""
        token_start = token.idx
        token_end = token_start + len(token.text)

        search_start = max(0, token_start - window_size)
        search_end = min(len(text), token_end + window_size)

        return text[search_start:search_end]
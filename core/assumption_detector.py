"""
Assumption Detection Module

This module detects implicit assumptions in requirements and test cases that
are not explicitly stated. These hidden assumptions can lead to flaky tests
and rework during automation.

Detects assumptions in three categories:
- Environment assumptions (browser, OS, device, network)
- Data assumptions (valid users, credentials, test data)
- State assumptions (user logged in, feature enabled, permissions)
"""

import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass

import spacy
from spacy.tokens import Doc


@dataclass
class AssumptionIssue:
    """Represents a detected assumption issue."""
    type: str
    category: str
    text: str
    message: str
    assumption: str


# Balanced assumption weights by category and severity
ASSUMPTION_WEIGHTS = {
    "Environment": {
        "UI interaction": 14,  # Browser/device assumptions critical
        "browsers": 12,
        "devices": 12,
        "operating_systems": 11,
        "network": 10,
        "display": 9,
        "databases": 15,      # Database assumptions very critical
        "apis": 12,
        "cloud_providers": 11
    },
    "Data": {
        "user_exists": 10,    # User data assumptions important
        "credentials_exist": 11, # Authentication data critical
        "form_filled": 8,
        "data_entered": 9,
        "record_exists": 9,
        "data_exists": 8,
        "file_exists": 9,
        "recipient_exists": 8,
        "sender_exists": 8,
        "task_exists": 8,
        "item_exists": 7,
        "issue_exists": 8
    },
    "State": {
        "user_logged_in": 13,    # Authentication state critical
        "permissions_granted": 14, # Authorization state most critical
        "condition_exists": 9,
        "error_trigger": 10,
        "failure_condition": 9,
        "admin_role": 11,
        "manager_role": 10,
        "user_role": 10,
        "account_active": 12,
        "form_valid": 8,
        "space_available": 8
    }
}


class AssumptionDetector:
    """
    Detects implicit assumptions in requirement text using rule-based inference.

    This detector identifies missing preconditions and context that are assumed
    but not explicitly stated in the requirements.
    """

    def __init__(self, nlp_model: str = "en_core_web_sm"):
        """
        Initialize the assumption detector.

        Args:
            nlp_model: spaCy language model to use (default: en_core_web_sm)
        """
        try:
            self.nlp = spacy.load(nlp_model)
        except OSError:
            # Fallback to blank model if en_core_web_sm not available
            self.nlp = spacy.blank("en")

        # Define action patterns that imply assumptions
        self.action_patterns = {
            # Authentication actions
            "login": ["user_exists", "credentials_exist"],
            "log in": ["user_exists", "credentials_exist"],
            "sign in": ["user_exists", "credentials_exist"],
            "authenticate": ["user_exists", "credentials_exist"],
            "logout": ["user_logged_in"],
            "log out": ["user_logged_in"],
            "sign out": ["user_logged_in"],

            # Navigation and access actions
            "navigate": ["user_logged_in"],
            "access": ["user_logged_in", "permissions_granted"],
            "view": ["user_logged_in", "permissions_granted"],
            "see": ["user_logged_in", "permissions_granted"],
            "visit": ["user_logged_in"],
            "go to": ["user_logged_in"],
            "open": ["user_logged_in"],
            "enter": ["user_logged_in"],
            "browse": ["user_logged_in"],

            # Data manipulation actions
            "submit": ["form_filled", "user_logged_in"],
            "save": ["data_entered", "user_logged_in"],
            "update": ["record_exists", "user_logged_in", "permissions_granted"],
            "delete": ["record_exists", "user_logged_in", "permissions_granted"],
            "edit": ["record_exists", "user_logged_in", "permissions_granted"],
            "modify": ["record_exists", "user_logged_in", "permissions_granted"],
            "create": ["user_logged_in", "permissions_granted"],
            "add": ["user_logged_in", "permissions_granted"],
            "insert": ["user_logged_in", "permissions_granted"],

            # Search and filter actions
            "search": ["user_logged_in"],
            "filter": ["user_logged_in"],
            "sort": ["user_logged_in"],
            "find": ["user_logged_in"],
            "query": ["user_logged_in"],
            "lookup": ["user_logged_in"],

            # Verification and validation actions
            "verify": ["condition_exists", "user_logged_in"],
            "check": ["condition_exists", "user_logged_in"],
            "validate": ["data_exists", "user_logged_in"],
            "confirm": ["condition_exists", "user_logged_in"],
            "ensure": ["condition_exists", "user_logged_in"],
            "assert": ["condition_exists", "user_logged_in"],
            "test": ["condition_exists", "user_logged_in"],

            # File operations
            "upload": ["file_exists", "user_logged_in"],
            "download": ["file_exists", "user_logged_in", "permissions_granted"],
            "export": ["data_exists", "user_logged_in"],
            "import": ["file_exists", "user_logged_in", "permissions_granted"],
            "attach": ["file_exists", "user_logged_in"],
            "share": ["file_exists", "user_logged_in", "permissions_granted"],

            # Communication actions
            "send": ["recipient_exists", "user_logged_in"],
            "receive": ["sender_exists"],
            "message": ["communication_setup"],
            "email": ["recipient_exists", "user_logged_in"],
            "notify": ["recipient_exists", "user_logged_in"],
            "contact": ["recipient_exists", "user_logged_in"],
            "communicate": ["communication_setup"],

            # User role specific actions
            "admin": ["admin_role", "user_logged_in"],
            "manager": ["manager_role", "user_logged_in"],
            "administrator": ["admin_role", "user_logged_in"],
            "supervisor": ["manager_role", "user_logged_in"],

            # Error and failure handling
            "error": ["error_trigger"],
            "fail": ["failure_condition"],
            "crash": ["error_trigger"],
            "break": ["error_trigger"],
            "handle": ["error_trigger"],
            "recover": ["failure_condition"],

            # Configuration and settings
            "configure": ["admin_role", "user_logged_in"],
            "setup": ["admin_role", "user_logged_in"],
            "customize": ["user_logged_in"],
            "personalize": ["user_logged_in"],
            "settings": ["user_logged_in"],
            "preferences": ["user_logged_in"],

            # Reporting and analytics
            "report": ["data_exists", "user_logged_in", "permissions_granted"],
            "analytics": ["data_exists", "user_logged_in", "permissions_granted"],
            "dashboard": ["user_logged_in"],
            "metrics": ["data_exists", "user_logged_in", "permissions_granted"],
            "statistics": ["data_exists", "user_logged_in", "permissions_granted"],

            # Integration and API actions
            "integrate": ["external_service_exists"],
            "connect": ["external_service_exists"],
            "sync": ["external_service_exists"],
            "api": ["api_access_configured"],
            "webhook": ["webhook_configured"],
            "callback": ["callback_configured"]
        }

        # Define assumption descriptions
        self.assumption_descriptions = {
            "user_exists": "Valid test user exists in the system",
            "credentials_exist": "User credentials are available and valid",
            "user_logged_in": "User is already authenticated/logged in",
            "permissions_granted": "User has necessary permissions for the action",
            "form_filled": "Form is already filled with valid data",
            "data_entered": "Required data has been entered",
            "record_exists": "Target record exists in the system",
            "condition_exists": "Condition to verify is present",
            "data_exists": "Required data exists for validation",
            "error_trigger": "Error condition can be triggered",
            "failure_condition": "Failure scenario can be reproduced",
            "admin_role": "Admin user role is available",
            "manager_role": "Manager user role is available",
            "user_role": "Regular user role is available",
            "file_exists": "Required file exists for the operation",
            "recipient_exists": "Message recipient exists",
            "sender_exists": "Message sender exists",
            "communication_setup": "Communication channel is configured",
            "external_service_exists": "External service or API is available and accessible",
            "api_access_configured": "API access credentials and endpoints are configured",
            "webhook_configured": "Webhook endpoints are set up and accessible",
            "callback_configured": "Callback mechanisms are properly configured"
        }

        # Environment assumptions that should be explicit
        self.environment_indicators = {
            "browser", "chrome", "firefox", "safari", "edge",
            "mobile", "desktop", "tablet", "ios", "android",
            "windows", "mac", "linux", "device", "network"
        }

    def detect_assumptions(self, text: str) -> List[AssumptionIssue]:
        """
        Detect all implicit assumptions in the given text.

        Args:
            text: Input requirement or test case text

        Returns:
            List of AssumptionIssue objects with detected assumptions
        """
        issues = []

        # Process text with spaCy
        doc = self.nlp(text.lower())

        # Detect action-based assumptions
        issues.extend(self._detect_action_assumptions(doc, text))

        # Detect missing environment specifications
        issues.extend(self._detect_environment_assumptions(text))

        # Detect data and state assumptions from context
        issues.extend(self._detect_context_assumptions(text))

        return issues

    def _detect_action_assumptions(self, doc: Doc, original_text: str) -> List[AssumptionIssue]:
        """Detect assumptions implied by specific actions mentioned in text."""
        issues = []
        text_lower = original_text.lower()

        for action, assumptions in self.action_patterns.items():
            if action in text_lower:
                for assumption_key in assumptions:
                    if not self._is_assumption_explicit(text_lower, assumption_key):
                        issues.append(AssumptionIssue(
                            type="Action assumption",
                            category=self._get_assumption_category(assumption_key),
                            text=action,
                            message=f"Action '{action}' implies assumption",
                            assumption=self.assumption_descriptions.get(assumption_key, assumption_key)
                        ))

        return issues

    def _detect_environment_assumptions(self, text: str) -> List[AssumptionIssue]:
        """Detect missing environment specifications."""
        issues = []
        text_lower = text.lower()

        # Check for UI interactions without environment specification
        ui_actions = ["click", "type", "select", "scroll", "hover", "tap"]
        has_ui_action = any(action in text_lower for action in ui_actions)

        if has_ui_action:
            # Check if any environment is mentioned
            has_environment = any(env in text_lower for env in self.environment_indicators)

            if not has_environment:
                issues.append(AssumptionIssue(
                    type="Environment assumption",
                    category="Environment",
                    text="UI interaction",
                    message="UI interaction without environment specification",
                    assumption="Browser, device, or platform is specified"
                ))

        return issues

    def _detect_context_assumptions(self, text: str) -> List[AssumptionIssue]:
        """Detect assumptions from broader context patterns."""
        issues = []
        text_lower = text.lower()

        # Check for user-specific actions without user context
        user_actions = ["profile", "settings", "account", "dashboard"]
        if any(action in text_lower for action in user_actions):
            if not self._has_user_context(text_lower):
                issues.append(AssumptionIssue(
                    type="Context assumption",
                    category="State",
                    text="User-specific action",
                    message="User-specific action without user context",
                    assumption="User is logged in and authenticated"
                ))

        # Check for data operations without data context
        data_actions = ["search", "filter", "sort", "export"]
        if any(action in text_lower for action in data_actions):
            if not self._has_data_context(text_lower):
                issues.append(AssumptionIssue(
                    type="Context assumption",
                    category="Data",
                    text="Data operation",
                    message="Data operation without data context",
                    assumption="Required data exists in the system"
                ))

        return issues

    def _is_assumption_explicit(self, text: str, assumption_key: str) -> bool:
        """
        Check if an assumption is explicitly stated in the text.

        This is a simple keyword-based check. In production, this could be
        enhanced with more sophisticated NLP.
        """
        explicit_indicators = {
            "user_exists": ["user exists", "test user", "valid user"],
            "credentials_exist": ["credentials", "password", "login details"],
            "user_logged_in": ["logged in", "authenticated", "signed in"],
            "permissions_granted": ["permission", "authorized", "access granted"],
            "form_filled": ["filled", "entered", "completed"],
            "data_entered": ["entered", "provided", "input"],
            "record_exists": ["exists", "available", "present"],
            "condition_exists": ["condition", "scenario", "case"],
            "data_exists": ["data exists", "available data"],
            "error_trigger": ["error occurs", "error condition"],
            "failure_condition": ["failure", "error case"],
        }

        indicators = explicit_indicators.get(assumption_key, [])
        return any(indicator in text for indicator in indicators)

    def _get_assumption_category(self, assumption_key: str) -> str:
        """Map assumption key to category."""
        category_mapping = {
            "user_exists": "Data",
            "credentials_exist": "Data",
            "user_logged_in": "State",
            "permissions_granted": "State",
            "form_filled": "Data",
            "data_entered": "Data",
            "record_exists": "Data",
            "condition_exists": "State",
            "data_exists": "Data",
            "error_trigger": "State",
            "failure_condition": "State",
            "admin_role": "State",
            "manager_role": "State",
            "user_role": "State",
            "file_exists": "Data",
            "recipient_exists": "Data",
            "sender_exists": "Data",
            "communication_setup": "Environment",
            "external_service_exists": "Environment",
            "api_access_configured": "Environment",
            "webhook_configured": "Environment",
            "callback_configured": "Environment"
        }

        return category_mapping.get(assumption_key, "Unknown")

    def _has_user_context(self, text: str) -> bool:
        """Check if text has explicit user context."""
        user_indicators = [
            "user", "login", "authenticate", "sign in", "logged in",
            "account", "profile", "session"
        ]
        return any(indicator in text for indicator in user_indicators)

    def _has_data_context(self, text: str) -> bool:
        """Check if text has explicit data context."""
        data_indicators = [
            "data", "record", "entry", "information", "content",
            "database", "exists", "available", "present"
        ]
        return any(indicator in text for indicator in data_indicators)

    def calculate_assumption_score(self, issues: List[AssumptionIssue], text: str = "") -> Dict[str, Any]:
        """
        Calculate multi-signal assumption score with component breakdown and strength classification.

        Returns detailed scoring with three components:
        - environment_assumptions_score: environment/data infrastructure assumptions
        - data_assumptions_score: test data and user assumptions
        - state_assumptions_score: system state and permissions assumptions

        Each component includes count and strength classification (STRONG/WEAK).

        Args:
            issues: List of detected assumption issues
            text: Original text for context analysis

        Returns:
            Dictionary with overall score and component details
        """
        if not issues:
            return {
                "score": 0.0,
                "components": {
                    "environment": {"count": 0, "strength": "NONE"},
                    "data": {"count": 0, "strength": "NONE"},
                    "state": {"count": 0, "strength": "NONE"}
                }
            }

        # Categorize issues by component
        environment_issues = [issue for issue in issues if issue.category == "Environment"]
        data_issues = [issue for issue in issues if issue.category == "Data"]
        state_issues = [issue for issue in issues if issue.category == "State"]

        # Calculate component scores and strengths
        environment_score, environment_strength = self._calculate_component_with_strength(environment_issues, "Environment")
        data_score, data_strength = self._calculate_component_with_strength(data_issues, "Data")
        state_score, state_strength = self._calculate_component_with_strength(state_issues, "State")

        # Overall score: weighted average (State most critical, then Environment, then Data)
        overall_score = (environment_score * 0.35 + data_score * 0.25 + state_score * 0.4)

        return {
            "score": round(overall_score, 1),
            "components": {
                "environment": {
                    "count": len(environment_issues),
                    "strength": environment_strength
                },
                "data": {
                    "count": len(data_issues),
                    "strength": data_strength
                },
                "state": {
                    "count": len(state_issues),
                    "strength": state_strength
                }
            }
        }

    def _calculate_component_with_strength(self, component_issues: List[AssumptionIssue], component_type: str) -> Tuple[float, str]:
        """Calculate score and strength for a specific assumption component."""
        if not component_issues:
            return 0.0, "NONE"

        base_weights = ASSUMPTION_WEIGHTS
        base_score = 0
        has_strong_assumption = False
        has_weak_assumption = False

        for issue in component_issues:
            # Determine strength classification
            strength = self._classify_assumption_strength(issue, component_type)
            if strength == "STRONG":
                has_strong_assumption = True
            else:
                has_weak_assumption = True

            # Get weight for this assumption type
            if component_type in base_weights and isinstance(base_weights[component_type], dict):
                weight = self._get_assumption_type_weight(issue, base_weights[component_type])
            else:
                weight = base_weights.get(component_type, 10)
            base_score += weight

        # Multiple assumptions increase score
        if len(component_issues) > 1:
            base_score += (len(component_issues) - 1) * 5

        # Calculate density factor for this component
        text_length = 50  # Will be passed from main method if needed
        density_factor = len(component_issues) / max(text_length, 5)

        # Component-specific density scoring
        if component_type == "State":
            density_score = min(30, density_factor * 60)  # State assumptions most critical
        elif component_type == "Environment":
            density_score = min(25, density_factor * 50)  # Environment assumptions critical
        else:  # Data
            density_score = min(20, density_factor * 40)  # Data assumptions less critical

        raw_score = base_score + density_score

        # Conservative normalization
        if raw_score > 70:
            final_score = 70 + (raw_score - 70) * 0.4
        else:
            final_score = raw_score

        final_score = min(100.0, final_score)

        # Determine overall strength for component
        if has_strong_assumption:
            strength = "STRONG"
        elif has_weak_assumption:
            strength = "WEAK"
        else:
            strength = "UNKNOWN"

        return final_score, strength

    def _classify_assumption_strength(self, issue: AssumptionIssue, component_type: str) -> str:
        """Classify an assumption as STRONG or WEAK based on its type and context."""
        assumption_text = issue.assumption.lower()

        # STRONG assumptions (very likely to break automation)
        strong_patterns = {
            "Environment": [
                "browser", "device", "operating system", "database", "api", "network",
                "server", "infrastructure", "platform", "environment"
            ],
            "State": [
                "user logged in", "authenticated", "authorized", "permissions granted",
                "admin role", "session active", "account active", "system configured"
            ],
            "Data": [
                "user exists", "credentials exist", "test data prepared", "database populated",
                "external service available", "api endpoint configured"
            ]
        }

        # WEAK assumptions (contextual or optional)
        weak_patterns = {
            "Environment": [
                "internet connection", "power available", "display resolution"
            ],
            "State": [
                "user preferences set", "notifications enabled", "theme selected"
            ],
            "Data": [
                "sample data", "demo content", "placeholder text", "optional fields"
            ]
        }

        # Check for strong patterns first
        if component_type in strong_patterns:
            for pattern in strong_patterns[component_type]:
                if pattern in assumption_text:
                    return "STRONG"

        # Check for weak patterns
        if component_type in weak_patterns:
            for pattern in weak_patterns[component_type]:
                if pattern in assumption_text:
                    return "WEAK"

        # Default classification based on component type
        if component_type == "Environment":
            return "STRONG"  # Environment assumptions are usually critical
        elif component_type == "State":
            return "STRONG"  # State assumptions are usually critical
        else:
            return "WEAK"    # Data assumptions can be more flexible

    def _get_assumption_type_weight(self, issue: AssumptionIssue, type_weights: dict) -> float:
        """Get weight for specific assumption types."""
        assumption_key = issue.assumption.lower()

        # Direct mapping for common assumption types
        key_mappings = {
            "user exists": "user_exists",
            "credentials exist": "credentials_exist",
            "user logged in": "user_logged_in",
            "permissions granted": "permissions_granted",
            "form filled": "form_filled",
            "data entered": "data_entered",
            "record exists": "record_exists",
            "data exists": "data_exists",
            "condition exists": "condition_exists",
            "file exists": "file_exists",
            "recipient exists": "recipient_exists",
            "sender exists": "sender_exists",
            "task exists": "task_exists",
            "item exists": "item_exists",
            "issue exists": "issue_exists",
            "error trigger": "error_trigger",
            "failure condition": "failure_condition",
            "admin role": "admin_role",
            "manager role": "manager_role",
            "user role": "user_role",
            "account active": "account_active",
            "form valid": "form_valid",
            "space available": "space_available"
        }

        for phrase, key in key_mappings.items():
            if phrase in assumption_key:
                return type_weights.get(key, 15)  # Default to category average

        # Check for environment indicators
        if any(word in assumption_key for word in ['browser', 'chrome', 'firefox', 'safari', 'edge']):
            return type_weights.get('browsers', 20)
        elif any(word in assumption_key for word in ['mobile', 'desktop', 'tablet', 'phone']):
            return type_weights.get('devices', 20)
        elif any(word in assumption_key for word in ['ios', 'android', 'windows', 'mac', 'linux']):
            return type_weights.get('operating_systems', 18)
        elif any(word in assumption_key for word in ['network', 'wifi', 'cellular', 'broadband']):
            return type_weights.get('network', 16)
        elif any(word in assumption_key for word in ['database', 'mysql', 'postgresql', 'mongodb']):
            return type_weights.get('databases', 24)
        elif any(word in assumption_key for word in ['api', 'endpoint', 'rest', 'graphql']):
            return type_weights.get('apis', 20)

        return 15  # Default weight for unspecified assumption types
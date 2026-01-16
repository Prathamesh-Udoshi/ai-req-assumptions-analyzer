"""
Streamlit Frontend for Intelligent Test Case Quality Analyzer

An interactive web interface for analyzing test case quality and assumptions.
Built with Streamlit for rapid prototyping and easy deployment.
"""

import streamlit as st
import requests
import json
import pandas as pd
import time
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go


# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this for production
DEFAULT_EXAMPLES = [
    "The system should load fast and handle errors properly",
    "User logs in with valid credentials and accesses dashboard",
    "Click the submit button and verify error message appears",
    "The application must respond quickly to user interactions",
    "Given user is logged in, when clicking save, then data should persist",
    "System should be scalable and handle up to 1000 concurrent users",
    "Navigate to user profile page and update personal information"
]


class RequirementsAnalyzer:
    """Frontend interface for the requirements analysis API."""

    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a single requirement text."""
        try:
            response = requests.post(
                f"{self.api_url}/analyze",
                json={"text": text},
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            return result

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Make sure the FastAPI server is running on http://localhost:8000")
            st.info("Start the server with: `python app.py`")
            return None
        except requests.exceptions.Timeout:
            st.error("⏰ API request timed out. The server might be overloaded.")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"🔴 HTTP Error: {e.response.status_code} - {e.response.reason}")
            try:
                error_detail = e.response.json()
                st.error(f"Details: {error_detail}")
            except:
                st.error(f"Response: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"📡 Network Error: {str(e)}")
            return None
        except ValueError as e:
            st.error(f"📄 JSON Parse Error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"💥 Unexpected Error: {str(e)}")
            return None

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple requirements in batch."""
        try:
            response = requests.post(
                f"{self.api_url}/analyze/batch",
                json={"texts": texts},
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            st.error(f"Batch API Error: {str(e)}")
            return []

    def health_check(self) -> bool:
        """Check if the API is available."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False


def main():
    """Main Streamlit application."""

    # Page configuration
    st.set_page_config(
        page_title="Intelligent Test Case Analyzer",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling and new UI elements
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-summary {
        font-size: 1.2rem;
        font-weight: 500;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .confidence-indicator {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6c757d;
        margin-bottom: 1rem;
    }
    .component-breakdown {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .critical-assumptions {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .minor-assumptions {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .clarifying-questions {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .ready-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .needs-clarification-badge {
        background-color: #ffc107;
        color: black;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .high-risk-badge {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .impact-issue {
        background-color: #fff;
        border: 1px solid #dee2e6;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="main-header">🎯 Intelligent Test Case Quality Analyzer</div>', unsafe_allow_html=True)
    st.markdown("**Trustworthy analysis of test case quality - ensure automation-ready test cases**")

    # Initialize analyzer
    analyzer = RequirementsAnalyzer()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # API Status
        if analyzer.health_check():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Not Available")
            st.info("Make sure the FastAPI server is running on port 8000")

        st.markdown("---")

        # Navigation
        page = st.radio(
            "Choose Analysis Mode:",
            ["Single Test Analysis", "Batch Test Analysis", "Quality Dashboard"],
            index=0
        )

        st.markdown("---")

        # Examples
        with st.expander("📝 Example Requirements"):
            for example in DEFAULT_EXAMPLES:
                if st.button(f"Use: {example[:50]}...", key=example):
                    st.session_state.requirement_text = example
                    st.rerun()

    # Main content based on selected page
    if page == "Single Test Analysis":
        show_single_analysis(analyzer)
    elif page == "Batch Test Analysis":
        show_batch_analysis(analyzer)
    else:  # Quality Dashboard
        show_dashboard(analyzer)


def show_single_analysis(analyzer: RequirementsAnalyzer):
    """Single test case analysis page."""

    st.header("📄 Single Test Case Analysis")

    # Initialize session state for text input
    if 'requirement_text' not in st.session_state:
        st.session_state.requirement_text = ""

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        # Text input
        requirement_text = st.text_area(
            "Enter your test case or requirement:",
            value=st.session_state.requirement_text,
            height=100,
            placeholder="Example: User logs in with valid credentials and accesses dashboard",
            key="main_text_area"
        )

        # Update session state when text changes
        if requirement_text != st.session_state.requirement_text:
            st.session_state.requirement_text = requirement_text

    with col2:
        st.markdown("**Quick Examples:**")
        for i, example in enumerate(DEFAULT_EXAMPLES[:3]):
            if st.button(f"Ex {i+1}", key=f"quick_{i}"):
                st.session_state.requirement_text = example
                st.rerun()

    # Input validation
    text_length = len(requirement_text.strip())
    if text_length > 0 and text_length < 10:
        st.warning("⚠️ Very short text detected. Analysis confidence may be lower.")
    elif text_length > 500:
        st.info("📝 Long text detected. Consider breaking into smaller, focused test cases.")

    # Analysis button
    if st.button("🎯 Analyze Test Quality", type="primary", use_container_width=True):
        text_to_analyze = requirement_text.strip()

        if not text_to_analyze:
            st.error("Please enter some text to analyze.")
            return

        with st.spinner("🔍 Analyzing test case quality..."):
            result = analyzer.analyze_text(text_to_analyze)

        if result:
            st.success("✅ Test quality analysis completed!")
            display_analysis_result(text_to_analyze, result)
        else:
            st.error("❌ Analysis failed. Please check the API connection and try again.")
            st.info("💡 Make sure the FastAPI server is running on http://localhost:8000")


def show_batch_analysis(analyzer: RequirementsAnalyzer):
    """Batch test analysis page."""

    st.header("📊 Batch Test Analysis")

    st.markdown("Analyze multiple test cases at once for efficient quality assessment and automation planning.")

    # Input method
    input_method = st.radio(
        "Choose input method:",
        ["Manual Entry", "CSV Upload", "Sample Data"],
        horizontal=True
    )

    requirements = []

    if input_method == "Manual Entry":
        # Multi-line text input
        batch_text = st.text_area(
            "Enter requirements (one per line):",
            height=200,
            placeholder="Enter each requirement on a new line...\n\nExample:\nThe system should load fast\nUser logs in with valid credentials\nClick submit button"
        )

        if batch_text.strip():
            requirements = [line.strip() for line in batch_text.split('\n') if line.strip()]

    elif input_method == "CSV Upload":
        # File upload
        uploaded_file = st.file_uploader(
            "Upload CSV file with requirements",
            type=['csv'],
            help="CSV should have a 'text' column containing requirements"
        )

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                if 'text' in df.columns:
                    requirements = df['text'].dropna().tolist()
                    st.success(f"Loaded {len(requirements)} requirements from CSV")
                else:
                    st.error("CSV must contain a 'text' column")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    else:  # Sample Data
        try:
            df = pd.read_csv("../data/sample_requirements.csv")
            requirements = df['text'].tolist()[:10]  # First 10 samples
            st.info(f"Using {len(requirements)} sample requirements")
        except:
            requirements = DEFAULT_EXAMPLES
            st.info(f"Using {len(requirements)} default examples")

    # Show requirements preview
    if requirements:
        with st.expander(f"📋 Requirements to Analyze ({len(requirements)})"):
            for i, req in enumerate(requirements, 1):
                st.write(f"{i}. {req}")

    # Analyze button
    if st.button("🔍 Analyze Test Batch", type="primary", use_container_width=True):
        if not requirements:
            st.error("No requirements to analyze.")
            return

        with st.spinner(f"Analyzing {len(requirements)} requirements..."):
            results = analyzer.analyze_batch(requirements)

        if results:
            display_batch_results(requirements, results)


def show_dashboard(analyzer: RequirementsAnalyzer):
    """Dashboard with test quality analytics and insights."""

    st.header("📈 Test Quality Dashboard")

    st.markdown("Analyze trends and quality metrics across your requirements.")

    # Load sample data for demo
    try:
        df = pd.read_csv("../data/sample_requirements.csv")
        sample_texts = df['text'].tolist()

        with st.spinner("Analyzing sample requirements..."):
            results = analyzer.analyze_batch(sample_texts[:20])  # Analyze first 20

        if results:
            display_dashboard_metrics(results)

    except Exception as e:
        st.error(f"Could not load sample data: {e}")
        st.info("Make sure the sample_requirements.csv file exists in the data directory")


def display_analysis_result(text: str, result: Dict[str, Any]):
    """Display analysis result with explanation-first UI design."""

    # 1. RISK SUMMARY FIRST - Most important message upfront
    st.markdown("### 🎯 Analysis Summary")
    st.caption("*Intelligent analysis of test automation readiness and quality risks*")

    readiness_score = round(result['readiness_score'])
    readiness_level = result['readiness_level']

    # Generate human-readable risk summary
    risk_message, risk_color = _get_risk_summary(readiness_score, readiness_level, result)

    # Display risk summary prominently
    if risk_color == "green":
        st.success(f"✅ {risk_message}")
    elif risk_color == "yellow":
        st.warning(f"⚠️ {risk_message}")
    else:
        st.error(f"🚨 {risk_message}")

    # 2. CONFIDENCE INDICATOR - Right after risk summary
    _display_confidence_indicator(result)

    # 3. MULTI-SIGNAL SCORE VISUALIZATION
    st.markdown("### 📊 Detailed Quality Analysis")
    st.caption("*Breakdown of different quality aspects for comprehensive assessment*")

    # Ambiguity components
    if 'ambiguity' in result and 'components' in result['ambiguity']:
        _display_ambiguity_breakdown(result['ambiguity'])

    # Assumption components
    if 'assumptions' in result and 'components' in result['assumptions']:
        _display_assumption_breakdown(result['assumptions'])

    # Overall readiness score (secondary, not primary)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Overall Readiness:** {readiness_score}/100")
        with st.expander("ℹ️ What does this mean?", expanded=False):
            st.markdown("""
            **Readiness Score** combines test quality analysis for automation planning:
            - **85+**: Well-prepared for test automation
            - **60-84**: Needs some clarification but generally automatable
            - **<60**: Significant issues need to be addressed before automation

            This score helps prioritize test cases for automation implementation.
            """)
    with col2:
        _display_readiness_badge(readiness_level)

    # 4. ISSUES WITH IMPACT FOCUS
    if result.get('issues'):
        st.markdown("### ⚠️ Quality Issues Found")
        st.caption("*Specific problems that could affect test automation success*")
        _display_impact_issues(result['issues'])

    # 5. CLARIFYING QUESTIONS AS PRIMARY CTA
    if result.get('clarifying_questions'):
        _display_clarifying_questions(result['clarifying_questions'])

    # 6. Original text (collapsed by default)
    with st.expander("📝 Original Test Case", expanded=False):
        st.write(text)


def _get_risk_summary(readiness_score: int, readiness_level: str, result: Dict) -> tuple[str, str]:
    """Generate human-readable risk summary based on analysis results."""

    if readiness_level == "Ready":
        if readiness_score >= 90:
            return "This test case looks solid for automation - low risk of flaky execution.", "green"
        else:
            return "This test case should work for automation, but consider the suggestions below.", "green"

    elif readiness_level == "Needs clarification":
        issue_count = len(result.get('issues', []))
        if issue_count > 3:
            return f"This test case needs clarification before automation ({issue_count} issues found).", "yellow"
        else:
            return "This test case could work but would benefit from clarification.", "yellow"

    else:  # High risk
        issue_count = len(result.get('issues', []))
        strong_assumptions = 0
        if 'assumptions' in result and 'components' in result['assumptions']:
            for component in result['assumptions']['components'].values():
                if isinstance(component, dict) and component.get('strength') == 'STRONG':
                    strong_assumptions += component.get('count', 0)

        if strong_assumptions > 0:
            return f"High risk for automation - {strong_assumptions} critical assumptions will cause test failures.", "red"
        else:
            return "High risk for automation - significant clarification needed to prevent flaky tests.", "red"


def _display_confidence_indicator(result: Dict[str, Any]):
    """Display confidence indicator with explanation."""

    confidence = "MEDIUM"  # Default fallback
    confidence_explanation = ""

    # Extract confidence from ambiguity analysis
    if 'ambiguity' in result and 'confidence' in result['ambiguity']:
        confidence = result['ambiguity']['confidence']

    # Generate explanation
    if confidence == "HIGH":
        confidence_explanation = "Analysis is based on clear signals and sufficient context"
        icon = "🟢"
        color = "green"
    elif confidence == "MEDIUM":
        confidence_explanation = "Analysis has moderate confidence - results should be reviewed"
        icon = "🟡"
        color = "orange"
    else:  # LOW
        confidence_explanation = "Analysis has low confidence - requirement is very short or lacks context"
        icon = "🔴"
        color = "red"

    st.markdown(f"**Analysis Confidence:** {icon} {confidence}")
    st.caption(confidence_explanation)
    st.markdown("---")


def _display_ambiguity_breakdown(ambiguity_data: Dict[str, Any]):
    """Display multi-signal ambiguity breakdown with explanations."""

    st.markdown("**Ambiguity Analysis**")
    st.caption("*How clear and specific is the language used?*")

    components = ambiguity_data.get('components', {})

    # Create progress bars for each component
    col1, col2, col3 = st.columns(3)

    with col1:
        lexical_score = components.get('lexical', 0)
        st.progress(lexical_score / 100)
        st.caption(f"**Lexical Issues:** {lexical_score}/100")
        with st.expander("ℹ️ What is this?", expanded=False):
            st.markdown("""
            **Lexical Issues** detect subjective or vague terms in test cases that can cause inconsistent execution:
            - Words like "fast", "user-friendly", "secure", "optimal"
            - Terms without measurable criteria or specific definitions
            - Subjective quality descriptors that lack concrete test assertions
            """)

    with col2:
        testability_score = components.get('testability', 0)
        st.progress(testability_score / 100)
        st.caption(f"**Testability Gaps:** {testability_score}/100")
        with st.expander("ℹ️ What is this?", expanded=False):
            st.markdown("""
            **Testability Gaps** identify test case steps that cannot be objectively verified:
            - Phrases like "works correctly", "handles properly", "performs well"
            - Test steps without specific acceptance criteria
            - Vague success conditions that can't be automated
            """)

    with col3:
        references_score = components.get('references', 0)
        st.progress(references_score / 100)
        st.caption(f"**Reference Issues:** {references_score}/100")
        with st.expander("ℹ️ What is this?", expanded=False):
            st.markdown("""
            **Reference Issues** find pronouns and references in test cases without clear antecedents:
            - Words like "it", "this", "that", "these", "those"
            - Unspecified UI elements, data fields, or system components
            - References that could point to multiple test objects
            """)


def _display_assumption_breakdown(assumptions_data: Dict[str, Any]):
    """Display multi-signal assumption breakdown with strength grouping and explanations."""

    st.markdown("**Assumption Analysis**")
    st.caption("*What preconditions or dependencies are implied?*")

    components = assumptions_data.get('components', {})

    # Group by strength
    strong_assumptions = []
    weak_assumptions = []

    for component_name, component_data in components.items():
        if isinstance(component_data, dict):
            count = component_data.get('count', 0)
            strength = component_data.get('strength', 'UNKNOWN')

            if count > 0:
                if strength == 'STRONG':
                    strong_assumptions.append((component_name, count))
                elif strength == 'WEAK':
                    weak_assumptions.append((component_name, count))

    # Display strong assumptions first (most critical)
    if strong_assumptions:
        st.markdown("🚨 **Critical Assumptions** *(will break automation if missing)*")
        for component_name, count in strong_assumptions:
            component_display = component_name.replace('_', ' ').title()
            st.error(f"• **{component_display}**: {count} hidden dependencies")

            # Add explanation for each component type
            with st.expander(f"ℹ️ About {component_display} assumptions", expanded=False):
                if component_name == 'environment':
                    st.markdown("""
                    **Environment Assumptions** require specific test environment setup:
                    - Browser or device compatibility for test execution
                    - Operating system requirements for test runners
                    - Network or connectivity needs for test data
                    - Database or external service availability for test scenarios
                    """)
                elif component_name == 'data':
                    st.markdown("""
                    **Data Assumptions** require test data to be prepared for execution:
                    - User accounts or credentials for authentication tests
                    - Sample data or content for validation scenarios
                    - Database state or records for data-driven tests
                    - File uploads or attachments for file handling tests
                    """)
                elif component_name == 'state':
                    st.markdown("""
                    **State Assumptions** require system to be in specific condition for test execution:
                    - User authentication status for access tests
                    - Application configuration for feature tests
                    - Permission or access levels for authorization tests
                    - Previous actions or setup steps for workflow tests
                    """)
        st.markdown("")

    # Display weak assumptions
    if weak_assumptions:
        st.markdown("⚠️ **Minor Assumptions** *(may cause issues but less critical)*")
        for component_name, count in weak_assumptions:
            component_display = component_name.replace('_', ' ').title()
            st.warning(f"• **{component_display}**: {count} contextual dependencies")

            # Add explanation for each component type
            with st.expander(f"ℹ️ About {component_display} assumptions", expanded=False):
                if component_name == 'environment':
                    st.markdown("""
                    **Minor Environment Assumptions** are contextual preferences:
                    - Preferred but not required browser versions
                    - Optional display or resolution settings
                    - Performance expectations without hard requirements
                    """)
                elif component_name == 'data':
                    st.markdown("""
                    **Minor Data Assumptions** are flexible requirements:
                    - Optional data formats or content types
                    - Sample data that's nice-to-have but not essential
                    - Default values or placeholders
                    """)
                elif component_name == 'state':
                    st.markdown("""
                    **Minor State Assumptions** are implicit preferences:
                    - Default user interface states
                    - Optional notification or display preferences
                    - Non-critical application configurations
                    """)
        st.markdown("")

    # Show if no assumptions found
    if not strong_assumptions and not weak_assumptions:
        st.success("✅ No significant assumptions detected")
        st.caption("*The requirement appears self-contained with explicit dependencies*")


def _display_readiness_badge(readiness_level: str):
    """Display readiness level badge."""
    if readiness_level == "Ready":
        st.markdown('<div class="ready-badge">Ready</div>', unsafe_allow_html=True)
    elif readiness_level == "Needs clarification":
        st.markdown('<div class="needs-clarification-badge">Needs Work</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="high-risk-badge">High Risk</div>', unsafe_allow_html=True)


def _display_impact_issues(issues: List[Dict[str, Any]]):
    """Display issues with focus on impact and actionable information."""

    st.markdown("### ⚠️ Issues Found")

    # Group issues by type but focus on impact
    for issue in issues:
        issue_type = issue.get('type', 'Unknown')
        message = issue.get('message', '')
        impact = issue.get('impact', 'May cause testing issues')

        # Create expandable issue with impact focus
        with st.expander(f"**{issue_type}**: {message[:60]}{'...' if len(message) > 60 else ''}", expanded=False):
            st.markdown(f"**Issue:** {message}")

            if issue_type == "Assumption":
                category = issue.get('category', '')
                assumption = issue.get('assumption', '')
                if category:
                    st.markdown(f"**Category:** {category}")
                if assumption:
                    st.markdown(f"**Missing:** {assumption}")

            st.markdown(f"**Impact:** {impact}")
            st.markdown("---")


def _display_clarifying_questions(questions: List[str]):
    """Display clarifying questions as primary call-to-action."""

    st.markdown("### 🎯 Recommended Clarifications")
    st.caption("*Specific questions to ask stakeholders for better test automation*")

    if len(questions) == 0:
        st.success("✅ No clarification questions needed - requirement is clear!")
        return

    # Display as a checklist-style
    st.markdown("**Consider asking these questions before automation:**")
    for i, question in enumerate(questions, 1):
        st.markdown(f"**{i}.** {question}")

    st.info("💡 **Pro Tip:** Addressing these questions will make your automated tests more reliable and maintainable.")


def display_batch_results(texts: List[str], results: List[Dict[str, Any]]):
    """Display batch analysis results."""

    # Summary statistics
    valid_results = [r for r in results if isinstance(r, dict) and 'readiness_score' in r]

    if not valid_results:
        st.error("No valid results to display")
        return

    st.markdown("### 📊 Batch Analysis Summary")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    avg_ambiguity = sum(r.get('ambiguity', {}).get('score', 0) for r in valid_results) / len(valid_results)
    avg_assumption = sum(r.get('assumptions', {}).get('score', 0) for r in valid_results) / len(valid_results)
    avg_readiness = sum(r['readiness_score'] for r in valid_results) / len(valid_results)

    readiness_counts = {}
    for r in valid_results:
        level = r.get('readiness_level', 'Unknown')
        readiness_counts[level] = readiness_counts.get(level, 0) + 1

    with col1:
        st.metric("Average Ambiguity", f"{avg_ambiguity:.1f}")

    with col2:
        st.metric("Average Assumptions", f"{avg_assumption:.1f}")

    with col3:
        st.metric("Average Readiness", f"{avg_readiness:.1f}")

    with col4:
        most_common = max(readiness_counts, key=readiness_counts.get)
        st.metric("Most Common Status", most_common)

    # Readiness distribution
    st.markdown("### 🎯 Readiness Distribution")
    labels = list(readiness_counts.keys())
    values = list(readiness_counts.values())

    fig = px.pie(
        values=values,
        names=labels,
        title="Requirements Readiness Distribution",
        color_discrete_sequence=['#28a745', '#ffc107', '#dc3545']
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed results table
    st.markdown("### 📋 Detailed Results")

    table_data = []
    for i, (text, result) in enumerate(zip(texts, results)):
        if isinstance(result, dict):
            table_data.append({
                'ID': i + 1,
                'Text': text[:50] + '...' if len(text) > 50 else text,
                'Ambiguity': f"{result.get('ambiguity', {}).get('score', 0):.1f}",
                'Assumptions': f"{result.get('assumptions', {}).get('score', 0):.1f}",
                'Readiness': f"{result.get('readiness_score', 0):.1f}",
                'Status': result.get('readiness_level', 'Error'),
                'Issues': len(result.get('issues', []))
            })
        else:
            table_data.append({
                'ID': i + 1,
                'Text': text[:50] + '...' if len(text) > 50 else text,
                'Ambiguity': 'Error',
                'Assumptions': 'Error',
                'Readiness': 'Error',
                'Status': 'Error',
                'Issues': 0
            })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

    # Export option
    if st.button("📥 Export Results to CSV"):
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="test_case_analysis_results.csv",
            mime="text/csv",
            key="download_csv"
        )


def display_dashboard_metrics(results: List[Dict[str, Any]]):
    """Display dashboard metrics and charts."""

    valid_results = [r for r in results if isinstance(r, dict) and 'readiness_score' in r]

    if not valid_results:
        st.error("No valid results for dashboard")
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    total_reqs = len(valid_results)
    ready_count = sum(1 for r in valid_results if r.get('readiness_level') == 'Ready')
    clarification_count = sum(1 for r in valid_results if r.get('readiness_level') == 'Needs clarification')
    high_risk_count = sum(1 for r in valid_results if r.get('readiness_level') == 'High risk for automation')

    with col1:
        st.metric("Total Requirements", total_reqs)

    with col2:
        ready_pct = (ready_count / total_reqs) * 100
        st.metric("Ready for Automation", f"{ready_pct:.1f}%")

    with col3:
        clarification_pct = (clarification_count / total_reqs) * 100
        st.metric("Needs Clarification", f"{clarification_pct:.1f}%")

    with col4:
        high_risk_pct = (high_risk_count / total_reqs) * 100
        st.metric("High Risk", f"{high_risk_pct:.1f}%")

    # Score distributions
    st.markdown("### 📈 Score Distributions")

    col1, col2 = st.columns(2)

    with col1:
        ambiguity_scores = [r.get('ambiguity', {}).get('score', 0) for r in valid_results]
        fig1 = px.histogram(
            ambiguity_scores,
            title="Ambiguity Score Distribution",
            labels={'value': 'Ambiguity Score'},
            color_discrete_sequence=['#ff6b6b']
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        readiness_scores = [r['readiness_score'] for r in valid_results]
        fig2 = px.histogram(
            readiness_scores,
            title="Readiness Score Distribution",
            labels={'value': 'Readiness Score'},
            color_discrete_sequence=['#45b7d1']
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Top issues
    st.markdown("### ⚠️ Most Common Issues")

    issue_counts = {}
    for result in valid_results:
        for issue in result.get('issues', []):
            issue_type = issue.get('type', 'Unknown')
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

    if issue_counts:
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        fig3 = px.bar(
            x=[item[0] for item in top_issues],
            y=[item[1] for item in top_issues],
            title="Most Common Issue Types",
            labels={'x': 'Issue Type', 'y': 'Count'},
            color_discrete_sequence=['#ffa726']
        )
        fig3.update_xaxes(tickangle=45)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No issues detected in the analyzed requirements!")


if __name__ == "__main__":
    main()
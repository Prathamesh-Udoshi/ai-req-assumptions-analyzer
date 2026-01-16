# Intelligent Test Case Quality Analyzer 🚀

An NLP-powered quality gate designed to analyze test cases and requirements. This tool identifies subjective language, weak modalities, and hidden assumptions to prevent flaky test automation and engineering rework.

---

## 🎯 Project Overview

This repository provides a production-ready solution for **Test Case Quality Assurance**. By leveraging `spaCy` and custom rule-based logic, it quantifies the automation-readiness of test cases and identifies quality issues before implementation.

### Key Capabilities
* **Multi-Signal Test Case Analysis**: Breaks down test case quality into lexical issues, testability gaps, and reference uncertainty with confidence indicators.
* **Automation Readiness Assessment**: Categorizes assumptions as STRONG (breaks automation) or WEAK (contextual) across environment, data, and state dimensions.
* **Trustworthy Quality Scoring**: Context-aware algorithms with human-calibrated weights and confidence levels (HIGH/MEDIUM/LOW).
* **Impact-Focused Test Feedback**: Every issue includes specific impact explanations and actionable clarification questions for automation.
* **Comprehensive Test Quality Assessment**: Quantified automation-readiness scores with detailed component breakdowns for data-driven test planning.

---

## 🏗️ Architecture & Implementation

The project is modularized to ensure separation of concerns, reflecting a "clean code" approach:

* **`core/`**: Advanced multi-signal test quality engine with context-aware rules, assumption strength classification, and confidence indicators.
* **`nlp/`**: Sophisticated pre-processing pipelines with spaCy POS tagging and dependency parsing for intelligent test case analysis.
* **`frontend/`**: Enhanced Streamlit UI with explanation-first design, multi-signal visualizations, and automation-focused feedback.
* **`data/`**: Comprehensive JSON configuration including human-calibrated weights, pattern libraries, and test case calibration datasets.

---

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **NLP**: `spaCy` (Rule-based matching and POS tagging)
* **Backend**: `FastAPI` / `Uvicorn`
* **Frontend**: `Streamlit`, `Flask`
* **Version Control**: `Git`

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher
* `pip` package manager

### Installation

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/Prathamesh-Udoshi/ai-req-assumptions-analyzer.git](https://github.com/Prathamesh-Udoshi/ai-req-assumptions-analyzer.git)
    cd req_quality_ai
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download the NLP model**:
    ```bash
    python -m spacy download en_core_web_sm
    ```

### Running the Application

To start the **FastAPI** backend:
```bash
python app.py
```


### 🚀 Launching the Enhanced Streamlit Interface

Experience the next-generation requirements quality analysis with our redesigned Streamlit interface:

```bash
streamlit run frontend/streamlit_app.py
```

**✨ New Features:**
- **Explanation-First UI**: Risk summaries appear before raw scores
- **Multi-Signal Visualizations**: Component breakdowns for ambiguity and assumptions
- **Confidence Indicators**: Trust levels for analysis reliability
- **Assumption Strength Classification**: Critical vs. minor dependencies
- **Impact-Focused Issues**: Why problems matter for automation success
- **Contextual Explanations**: Expandable help for all technical terms

### 🎯 Why This Approach Works

**Rule-Based NLP with Test Automation Intelligence:**
Unlike "black-box" ML models, our system combines rule-based NLP with human-calibrated weights and context-aware logic. Every decision is transparent and explainable, making it perfect for test automation teams who need to understand exactly why test cases need clarification before implementation.

**Key Differentiators:**
- **Multi-Signal Test Analysis**: Instead of single scores, provides component breakdowns for test quality
- **Confidence Quantification**: Tells you when test analysis is reliable vs. uncertain
- **Automation Impact Assessment**: Distinguishes assumptions that break test automation from minor ones
- **Test Failure Prevention**: Explains why issues matter for automation success and reliability
- **Calibration-Driven**: Weights tuned against human judgment of test case quality, not just data patterns

**Perfect for Test Automation Teams:**
- ✅ **Auditable**: Every flag has a clear rule and reasoning for test case approval
- ✅ **Adaptable**: Easy to customize for project-specific testing needs
- ✅ **Scalable**: Rule-based approach handles diverse test case patterns gracefully
- ✅ **Trustworthy**: Confidence indicators prevent over-reliance on uncertain test analysis
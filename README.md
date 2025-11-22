<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" />
  <img src="https://img.shields.io/badge/Streamlit-App-red.svg" />
  <img src="https://img.shields.io/badge/Google-Gemini%202.5%20Pro-brightgreen.svg" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  <img src="https://img.shields.io/badge/Agentic%20AI-Research%20Assistant-purple.svg" />
  <img src="https://img.shields.io/github/last-commit/Sudhanshu480/Enterprise_Research_Agent" />
  <img src="https://img.shields.io/github/repo-size/Sudhanshu480/Enterprise_Research_Agent" />
</p>

# 📘 Enterprise Company Research Agent

*A Conversational AI for Strategic Company Analysis & Account Plan Generation*

## 🚀 Project Overview

This project implements an **Agentic Conversational AI** that acts as a **Company Research Assistant**, capable of:
* Researching companies through natural conversation
* Pulling information from multiple external sources
* Generating complete, multi-section **strategic account plans**
* Handling confused, off-topic, and multi-persona users
* Allowing the user to **edit and regenerate** specific sections
* Providing **transparent tool logs** and data provenance
* Running inside an interactive **Streamlit UI**

_This work fulfills the **Eightfold.ai AI Agent Assignment** – *Problem Statement 1: Company Research Assistant (Account Plan Generator)*._

---

# 🎯 Features

### 🧠 Intelligent Conversational Agent
* **Natural Multi-turn Flow:** Context-aware memory allows for follow-up questions (e.g., "Who is the CEO?" after researching a company).
* **Intent Classification:** Intelligently categorizes inputs into `research`, `follow_up`, `compare`, `off_topic`, or `greeting`.
* **Persona-Aware:** Adapts to confused, chatty, or efficient users.
* **Powered by Gemini 2.5 Pro:** Utilizes advanced reasoning for high-fidelity output.

---

### 🌐 Multi-Source Information Gathering
The agent gathers and synthesizes information from:

| Source                           | Purpose                                                   |
| -------------------------------- | --------------------------------------------------------- |
| **Google Custom Search API**     | News, analysis, reports, company background               |
| **DuckDuckGo Search (Fallback)** | Ensures reliability even when CSE fails                   |
| **Yahoo Finance (yfinance)**     | Live market data, market cap, pricing, financial insights |

The system logs each tool invocation for transparency.

---

### 📝 Strategic Account Plan Generation
The model produces a structured enterprise-grade plan with sections:
* Executive Summary
* Product & Services Portfolio
* Market Analysis
* Financial Health
* SWOT Analysis
* Strategic Recommendations

Input → Web + Finance Data → Prompting → Markdown Report + Structured JSON

---

### 🔧 Interactive Plan Editor
The **Plan Editor** tab allows users to:
1.  Select any company researched during the session.
2.  View and modify the structured JSON data.
3.  **Regenerate the Report:** The agent rewrites the narrative report to reflect manual edits while maintaining professional formatting.
4.  **Dual Export:** Download the **Initial Report** (Raw AI) or the **Updated Report** (Human Edited) as PDFs.
<img width="1826" height="786" alt="image" src="https://github.com/user-attachments/assets/c694f5fb-777c-42bc-8048-69134cfc31ec" />


---

### 📊 Comparison Mode
Users can say:
```
Compare Tesla and BYD
```

The agent generates:
* A structured comparison
* A markdown table
* Key differentiators
* Summary insights
* The results look something like this:
  <img width="1714" height="687" alt="image" src="https://github.com/user-attachments/assets/e2d40d45-c8cc-47ea-a60e-345efdd49c3d" />
  <img width="1704" height="925" alt="image" src="https://github.com/user-attachments/assets/f65eacd3-5a9d-4509-8eb0-e90a79ef825f" />

---

### 📜 Transparent Logging
Every search query, API call, and model thought process is logged in the **"Tools & Logs"** tab, ensuring full explainability.

---

# 🏗️ System Architecture

```
+------------------------------------------------+
|                 Streamlit UI                   |
|    (Chat, Editor, Tools, PDF Download)         |
+------------------------+-----------------------+
                         |
                         v
+------------------------------------------------+
|                 Agent Controller               |
|           (CompanyResearchAgent)               |
+------------------------------------------------+
| Intent Classification  | Memory & Context      |
| Search Layer           | JSON Extraction       |
| Finance Layer          | Report Generator      |
| Comparison Engine      | Log Manager           |
+------------------------------------------------+
                         |
                         v
+-----------------------------+
| External Information APIs   |
+-----------------------------+
| Google Search API (CSE)     |
| DuckDuckGo Search(fallback) |
| yFinance (stock + market)   |
| Gemini 2.5 Pro (LLM)        |
+-----------------------------+
```

---

# 🧩 Core Files (Included in Repo)

### **1. `agent.py`**
The brain of the application. Contains the `CompanyResearchAgent` class, handling intent routing, tool execution, LLM interaction, and memory management.

### **2. `app.py`**
The Streamlit frontend. Manages the Chat UI, Plan Editor, PDF generation, and session state.

### **3. `requirements.txt`**
List of dependencies (`streamlit`, `google-generativeai`, `yfinance`, `fpdf`, etc.).

### **4. `.env`**
Configuration file for API keys (not included in repo).

---

# 🛠️ Setup Instructions

### 1. Clone Repo
```
git clone https://github.com/<your-username>/enterprise-research-agent
cd enterprise-research-agent
```

### 2. Create Virtual Environment
```
python -m venv venv
venv\Scripts\activate        # Windows
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Keys (Environment Variables)
Create a `.env` file in the project root and add the following:
```
GOOGLE_GENERATIVEAI_KEY=your_key_here
GOOGLE_API_KEY=your_google_cse_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

### 5. Run App
```
streamlit run app.py
```

---

# 🧠 Design Decisions (for evaluation)

### **1. Gemini 2.5 Pro for Analysis & Extraction**
Chosen for its strong reasoning abilities and structured output fidelity.

### **2. Two-Stage LLM Pipeline**
This ensures **accuracy + clean JSON extraction**:
* **Stage 1** → Detailed Markdown report
* **Stage 2** → JSON-only extraction (strict schema)

This significantly improves reliability vs one-shot generation.

### **3. Memory Engine**
Stores:
* Raw report text
* Original unmodified report
* Structured JSON
* Search & financial data provenance

### **4. Tool Layer Abstraction**
Search + financial + comparison + logging are isolated for better debugging.

### **5. Safety & Robustness**
* Filters invalid tickers
* Sanitizes URLs
* Falls back gracefully
* Model output cleaned before parsing

### **6. Streamlit UI Separation**
Agent logic is fully separated from UI for maintainability.

---

# 📦 Future Improvements
* Add vector memory (FAISS / ChromaDB)
* Voice mode using WebRTC
* Hybrid search (Google + Bing)
* Topic-specific risk analysis

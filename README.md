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

This work fulfills the **Eightfold.ai AI Agent Assignment** – *Problem Statement 1: Company Research Assistant (Account Plan Generator)*.

---

# 🎯 Features

### 🧠 Intelligent Conversational Agent
* Natural multi-turn conversation flow
* Intent classification:
  `research`, `follow_up`, `compare`, `off_topic`, `greeting`
* Persona-aware: confused users, chatty users, efficient users
* Error-tolerant, supported by Gemini 2.5 Pro

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

### 🔧 Editable Account Plans

The **Plan Editor** allows:

* Selecting any company researched so far
* Viewing structured JSON
* Editing individual sections
* Regenerating the ENTIRE report while maintaining professional formatting
* Downloading both **Initial** and **Updated** reports as PDF

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
* The results looks something like this:
  <img width="1714" height="687" alt="image" src="https://github.com/user-attachments/assets/e2d40d45-c8cc-47ea-a60e-345efdd49c3d" />
  <img width="1704" height="925" alt="image" src="https://github.com/user-attachments/assets/f65eacd3-5a9d-4509-8eb0-e90a79ef825f" />



---

### 📜 Tool Logging & Diagnostics

Every search, financial fetch, and model call is stored in:

```
🛠️ Tools & Logs
```

This is crucial for explainability and debugging.

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
+----------------------------+
| External Information APIs  |
+----------------------------+
| Google Search API (CSE)   |
| DuckDuckGo Search (fallback) |
| yFinance (stock + market) |
| Gemini 2.5 Pro (LLM)      |
+----------------------------+
```

---

# 🧩 Core Files (Included in Repo)

### **1. `agent.py`**

Core logic for search, financial analysis, LLM synthesis, JSON extraction, editing, and comparison.
Cited: 

### **2. `app.py`**

Streamlit frontend connecting user interactions to the agent.
Cited: 

### **3. `.env` (user-provided)**

Stores sensitive keys.

### **4. `requirements.txt`**

All dependencies (Streamlit, GenerativeAI, yfinance, DDGS, FPDF…).

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```
GOOGLE_GENERATIVEAI_KEY=your_key_here
GOOGLE_API_KEY=your_google_cse_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

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

### 4. Add `.env` File

Copy into project root.

### 5. Run App

```
streamlit run app.py
```

---

# 📡 Agentic Behaviours Implemented

### **✔ Confused User Handling**

If user writes:

> "Apple"
> Agent responds:
> “Do you mean Apple Inc. (tech) or Apple Bank?”
> and requests clarification.

### **✔ Efficient User Handling**

Quick, high-quality structured output.

### **✔ Chatty User Handling**

Stays focused, gently redirects conversation back to company analysis.

### **✔ Multi-Turn Memory**

Follow-up questions automatically continue referencing the last company.

### **✔ Error-Tolerant Behavior**

Handles:

* Missing tickers
* Blocked LLM responses
* Search failures
* Poor JSON formatting

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

# 🎥 Demo Scenarios (for your video)

**1. Efficient User**

> "Analyze Tesla"
> → Clean full report + JSON

**2. Confused User**

> “Apple”
> → Agent clarifies industry/type

**3. Chatty User**

> “Bro you won’t believe how tired I am, anyway research Reliance”
> → Agent stays professional, extracts intent

**4. Edge Case User**

> “Tell me how to cook pasta”
> → Polite refusal

**5. Multi-turn**

> “Analyze Amazon”
> “What about its cloud business?” (follow-up)
> → Contextual answers

**6. Editor Workflow**

* Edit SWOT → Regenerate full report
* Download updated PDF

**7. Comparison Demo**

> “Compare Nvidia and AMD”

---

# 🧪 Testing Done

✔ Multi-company switching
✔ JSON extraction reliability
✔ Long prompt stability
✔ Search + fallback reliability
✔ Streamlit rendering
✔ Error handling & messaging
✔ Persona handling

---

# 📦 Future Improvements

* Add vector memory (FAISS / ChromaDB)
* Voice mode using WebRTC
* Hybrid search (Google + Bing)
* Topic-specific risk analysis



Just tell me:
**“Add repo polish”**

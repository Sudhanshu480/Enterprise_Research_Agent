# agent.py
import os
import time
import json
import re
import requests
import logging
from typing import Any, Dict, List, Optional
import yfinance as yf
import google.generativeai as genai

# Fallback for DuckDuckGo
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# Configure logger
logger = logging.getLogger("company_agent")
logging.basicConfig(level=logging.INFO)

# --- HELPER FUNCTIONS ---
def safe_generate_text(model_instance, prompt, max_tokens=8192):
    """
    Reliably extracts text from Gemini.
    """
    try:
        resp = model_instance.generate_content(
            prompt, 
            generation_config={"max_output_tokens": max_tokens, "temperature": 0.3}
        )
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()
        if hasattr(resp, "candidates") and resp.candidates:
            parts = resp.candidates[0].content.parts
            return "".join([p.text for p in parts]).strip()
        return ""
    except Exception as exc:
        logger.error(f"Gemini API Error: {exc}")
        return f"Error generating content: {exc}"

def clean_json_string(json_str):
    """Helper to scrub Markdown formatting from JSON strings."""
    if "```json" in json_str:
        json_str = json_str.replace("```json", "").replace("```", "")
    elif "```" in json_str:
        json_str = json_str.replace("```", "")
    return json_str.strip()

class CompanyResearchAgent:
    def __init__(self, genai_api_key: str, google_api_key: Optional[str] = None, cse_id: Optional[str] = None):
        # 1. Validate Keys
        if not genai_api_key:
            raise ValueError("❌ API Key Error: GOOGLE_GENERATIVEAI_KEY is missing. Please check your .env file.")
        
        self.genai_api_key = genai_api_key
        self.google_api_key = google_api_key
        self.cse_id = cse_id
        
        self.model_name = "gemini-2.5-pro" 

        # Configure Gemini
        genai.configure(api_key=self.genai_api_key)
        self.model = genai.GenerativeModel(self.model_name)

        # Initialize State
        self.company_memory: Dict[str, Dict[str, Any]] = {}
        self.tool_calls: List[Dict[str, Any]] = []
        self.chat_history: List[Dict[str, str]] = []

    def _log_tool(self, tool: str, inp: Any, out: Any):
        """Log for the 'Tools' tab."""
        self.tool_calls.append({
            "tool": tool, 
            "input": str(inp)[:300], 
            "output": str(out)[:300], 
            "timestamp": time.time()
        })

    # --- SEARCH LAYER ---
    def search_web(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Attempts Google Custom Search -> Falls back to DuckDuckGo."""
        results = []
        
        # A. Try Google CSE
        if self.google_api_key and self.cse_id:
            try:
                url = "[https://www.googleapis.com/customsearch/v1](https://www.googleapis.com/customsearch/v1)"
                params = {"key": self.google_api_key, "cx": self.cse_id, "q": query, "num": top_k}
                res = requests.get(url, params=params, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    results = [{"title": i.get("title"), "link": i.get("link"), "snippet": i.get("snippet")} for i in data.get("items", [])]
                    self._log_tool("Google Search", query, f"Found {len(results)}")
                    return results
            except Exception as e:
                logger.warning(f"Google CSE failed: {e}")

        # B. Fallback to DuckDuckGo
        if DDGS:
            try:
                with DDGS() as ddgs:
                    raw_res = list(ddgs.text(query, max_results=top_k))
                    results = [{"title": r['title'], "link": r['href'], "snippet": r['body']} for r in raw_res]
                    self._log_tool("DuckDuckGo", query, f"Found {len(results)}")
                    return results
            except Exception as e:
                self._log_tool("Search Error", query, str(e))
        
        return []

    # --- FINANCIAL LAYER ---
    def fetch_financials(self, company: str) -> Dict[str, Any]:
        """Extracts ticker and fetches data via yfinance."""
        ticker = None
        
        match = re.search(r"\b[A-Z]{1,5}\b", company)
        if match: ticker = match.group(0)
        
        if not ticker:
            hits = self.search_web(f"{company} stock ticker symbol", top_k=1)
            if hits:
                m = re.search(r"\b([A-Z]{1,5})\b", hits[0].get("title", "").upper())
                if m: ticker = m.group(1)

        if not ticker:
            return {"error": "Could not detect ticker."}

        try:
            tk = yf.Ticker(ticker)
            data = {}
            # Heuristic: Try fast_info first, then info
            if hasattr(tk, 'fast_info') and tk.fast_info.last_price:
                data = {
                    "symbol": ticker,
                    "market_cap": tk.fast_info.market_cap,
                    "price": tk.fast_info.last_price,
                    "currency": tk.fast_info.currency,
                    "source": "yfinance fast_info"
                }
            elif tk.info and 'regularMarketPrice' in tk.info:
                 data = {
                    "symbol": ticker,
                    "market_cap": tk.info.get("marketCap"),
                    "sector": tk.info.get("sector"),
                    "summary": tk.info.get("longBusinessSummary", "")[:500]
                }
            else:
                return {"error": "No financial data available"}
                
            self._log_tool("YFinance", ticker, "Success")
            return data
        except Exception as e:
            return {"error": str(e)}

    # --- INTENT LAYER ---
    def classify_intent(self, user_text: str) -> Dict[str, Any]:
        """Decides what the user wants to do."""
        prompt = f"""
        Analyze: "{user_text}"
        
        Return valid JSON ONLY:
        {{
            "intent": "research" | "follow_up" | "compare" | "off_topic" | "greeting",
            "companies": ["List", "of", "companies"]
        }}
        """
        try:
            res = safe_generate_text(self.model, prompt, max_tokens=200)
            res = clean_json_string(res)
            if "{" in res:
                start = res.find("{")
                end = res.rfind("}") + 1
                return json.loads(res[start:end])
            return {"intent": "research", "companies": []}
        except:
            return {"intent": "research", "companies": []}

    # --- MAIN LOGIC ---
    def ask(self, user_text: str, status_callback=None) -> str:
        self.chat_history.append({"role": "user", "text": user_text})
        
        if status_callback: status_callback("🧠 Detecting intent...")
        intent_data = self.classify_intent(user_text)
        intent = intent_data.get("intent", "research")
        companies = intent_data.get("companies", [])

        if intent == "off_topic":
            return "I specialize in corporate strategy. Please ask me to research a company."
        
        if intent == "greeting":
            return "Hello! I am your Enterprise Research Agent. Ask me to 'Analyze Tesla' or 'Compare Ford and GM'."

        if intent == "compare" and len(companies) >= 2:
            return self.compare_companies(companies, status_callback)

        company = companies[0] if companies else user_text
        
        if intent == "follow_up" and self.company_memory:
             company = list(self.company_memory.keys())[-1]
             return self.answer_followup(company, user_text)

        return self.perform_deep_research(company, status_callback)

    def perform_deep_research(self, company_name: str, status_callback) -> str:
        if status_callback: status_callback(f"🌐 Searching global sources for {company_name}...")
        search_data = self.search_web(f"{company_name} strategic analysis news")
        
        if status_callback: status_callback(f"📈 Analyzing financial markets...")
        fin_data = self.fetch_financials(company_name)

        if status_callback: status_callback("📝 Writing Comprehensive Report (Step 1/2)...")
        
        # --- STEP 1: GENERATE TEXT REPORT ---
        report_prompt = f"""
        Role: Senior Strategy Consultant.
        Task: Create a COMPREHENSIVE Strategic Account Plan for '{company_name}'.
        
        Sources:
        Search: {json.dumps(search_data)[:3000]}
        Finance: {json.dumps(fin_data)}
        
        Instructions:
        1. Generate a detailed, multi-section report in Markdown.
        2. **IMPORTANT:** Do NOT include a title page, "Date:", "Prepared by:", or any introductory conversation.
        3. Start DIRECTLY with the first header (e.g., # Executive Summary).
        4. Sections required:
           - **Executive Summary**: High-level strategic overview.
           - **Product & Services Portfolio**: Detailed breakdown of offerings.
           - **Market Analysis**: Competitive landscape and position.
           - **Financial Health**: Analysis of the provided financial metrics.
           - **SWOT Analysis**: Detailed Strengths, Weaknesses, Opportunities, Threats.
           - **Strategic Recommendations**: Actionable next steps.
        """
        
        report_text = safe_generate_text(self.model, report_prompt, max_tokens=8000)
        
        if status_callback: status_callback("⚙️ Extracting Structured Data (Step 2/2)...")

        # --- STEP 2: EXTRACT JSON ONLY ---
        json_prompt = f"""
        You are a Data Extraction Specialist.
        
        INPUT TEXT:
        {report_text[:20000]} (Truncated for safety if extremely long)
        
        INSTRUCTIONS:
        Convert the insights from the text above into a valid JSON object.
        Do NOT include Markdown formatting (no ```json). Just the raw JSON string.
        
        JSON Structure:
        {{
            "company_name": "{company_name}",
            "overview": "Summary of the overview section...",
            "products_services": ["List of key products..."],
            "market_position": "Summary of market position...",
            "swot_analysis": {{ "strengths": [], "weaknesses": [], "opportunities": [], "threats": [] }},
            "strategic_recommendations": ["List of recommendations..."]
        }}
        """
        
        json_str = safe_generate_text(self.model, json_prompt, max_tokens=4000)
        json_str = clean_json_string(json_str)
        
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError:
            json_data = {"error": "Failed to parse JSON", "raw": json_str}
        
        # Store in memory - SAVING 'original_text' SEPARATELY
        self.company_memory[company_name] = {
            "text": report_text, 
            "original_text": report_text, # Keep a copy of the original
            "json": json_data
        }
        return report_text

    def answer_followup(self, company: str, question: str) -> str:
        mem = self.company_memory.get(company, {})
        context_text = mem.get('text', '')[:5000] 
        prompt = f"Context Report: {context_text}. User Question: {question}. Answer professionally."
        return safe_generate_text(self.model, prompt)

    def compare_companies(self, companies: List[str], status_callback) -> str:
        if status_callback: status_callback(f"⚖️ Comparing {', '.join(companies)}...")
        
        data_points = {}
        for c in companies:
            if c not in self.company_memory:
                self.perform_deep_research(c, None) 
            data_points[c] = self.company_memory[c].get("json")
            
        prompt = f"Compare these companies: {json.dumps(data_points)}. Output a Markdown table and key insights."
        return safe_generate_text(self.model, prompt)

    # --- EDITOR UTILS ---
    def list_companies(self): return list(self.company_memory.keys())
    def get_company_plan(self, c): return self.company_memory.get(c, {})
    def get_tool_calls(self): return self.tool_calls

    def update_company_section(self, company, section, new_val):
        mem = self.company_memory.get(company)
        if not mem: return "Error: Company not found"
        mem["json"][section] = new_val
        
        # Strict formatting, no filler.
        prompt = f"""
        The user has manually updated the '{section}' section of the account plan.
        Updated JSON Data: {json.dumps(mem['json'])}
        
        Task: Rewrite the FULL textual report to reflect this change.
        Constraints:
        1. STRICTLY maintain the original professional format.
        2. Do NOT include "Here is the updated report" or any conversational filler.
        3. Do NOT include dates or prepared by lines.
        4. Start directly with the Markdown content.
        """
        new_text = safe_generate_text(self.model, prompt, max_tokens=8000)
        mem["text"] = new_text
        return "Report Regenerated Successfully."
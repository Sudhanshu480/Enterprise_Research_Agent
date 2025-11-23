import streamlit as st
import os
import json
import time
from dotenv import load_dotenv 

load_dotenv()

# CHECKING KEYS BEFORE AGENT INITIALIZATION
api_key = os.getenv("GOOGLE_GENERATIVEAI_KEY")
if not api_key:
    st.error("❌ CRITICAL ERROR: GOOGLE_GENERATIVEAI_KEY not found in .env file.")
    st.stop()

# NOW IMPORT AGENT 
from agent import CompanyResearchAgent
from fpdf import FPDF

st.set_page_config(page_title="Enterprise Research Agent", page_icon="🧭", layout="wide")

st.markdown("""
<style>
    .stStatus { border-radius: 10px; background-color: #f0f2f6; }
    .chat-message { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- Init Agent ---
if "agent" not in st.session_state:
    try:
        # Initialize Agent
        st.session_state.agent = CompanyResearchAgent(
            genai_api_key=api_key,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            cse_id=os.getenv("GOOGLE_CSE_ID")
        )
    except Exception as e:
        st.error(f"Agent Init Error: {e}")
        st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Layout ---
st.title("🧭 Enterprise Strategy Agent")
st.markdown("---")

tabs = st.tabs(["💬 Research Chat", "📄 Plan Editor", "🛠️ Tools & Logs"])

# ==========================================
# TAB 1: CHAT
# ==========================================
with tabs[0]:
    st.info("💡 **Tip:** Try writing name of any Company for analysis. Agent uses **Gemini 2.5 Pro** for detailed analysis.")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    user_input = st.chat_input("Enter request...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.status("🤖 Agent working...", expanded=True) as status_box:
                def update_ui(message):
                    status_box.write(message)
                    time.sleep(0.1) 
                
                try:
                    response = st.session_state.agent.ask(user_input, status_callback=update_ui)
                    status_box.update(label="✅ Task Complete", state="complete", expanded=True)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "text": response})
                except Exception as e:
                    status_box.update(label="❌ Error", state="error", expanded=True)
                    st.error(f"Agent failed: {e}")

# ==========================================
# TAB 2: EDITOR
# ==========================================
with tabs[1]:
    companies = st.session_state.agent.list_companies()
    if not companies:
        st.info("👋 No research data yet. Please use the Chat tab first.")
    else:
        selected = st.selectbox("Select Company:", companies)
        plan = st.session_state.agent.get_company_plan(selected)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Live Report")
            st.markdown(plan.get("text", ""))
        
        with col2:
            st.subheader("Structured Data (Editable)")
            json_data = plan.get("json", {})
            
            keys = list(json_data.keys()) if isinstance(json_data, dict) else []
            if keys:
                section = st.selectbox("Edit Section:", keys)
                current_val = json_data[section]
                
                if isinstance(current_val, (dict, list)):
                    txt_val = st.text_area("Edit JSON", json.dumps(current_val, indent=2), height=300)
                    is_json = True
                else:
                    txt_val = st.text_area("Edit Text", str(current_val), height=300)
                    is_json = False
                
                # --- BUTTONS ---
                st.write("### Actions")
                
                # 1. Save Changes
                if st.button("💾 Commit Changes & Update Report"):
                    with st.spinner("Rewriting report..."):
                        try:
                            val = json.loads(txt_val) if is_json else txt_val
                            msg = st.session_state.agent.update_company_section(selected, section, val)
                            st.success(msg)
                            time.sleep(1) # Give user time to see success message
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                st.divider()
                
                # 2. Download Options
                d_col1, d_col2 = st.columns(2)
                
                with d_col1:
                    # Download ORIGINAL (Initial) Report
                    if st.button("📥 Download Initial Report (PDF)"):
                        try:
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            # Use 'original_text' from memory
                            original_text = plan.get("original_text", plan.get("text", ""))
                            clean_text = original_text.encode('latin-1', 'ignore').decode('latin-1')
                            pdf.multi_cell(0, 10, clean_text)
                            
                            # Helper to serve PDF
                            pdf.output(f"{selected}_Initial.pdf")
                            with open(f"{selected}_Initial.pdf", "rb") as f:
                                st.download_button(
                                    label="Click to Confirm Download (Initial)",
                                    data=f,
                                    file_name=f"{selected}_Initial_Report.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"PDF Error: {e}")

                with d_col2:
                    # Download UPDATED Report
                    if st.button("📥 Download Updated Report (PDF)"):
                        try:
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            # Use current 'text' from memory
                            current_text = plan.get("text", "")
                            clean_text = current_text.encode('latin-1', 'ignore').decode('latin-1')
                            pdf.multi_cell(0, 10, clean_text)
                            
                            pdf.output(f"{selected}_Updated.pdf")
                            with open(f"{selected}_Updated.pdf", "rb") as f:
                                st.download_button(
                                    label="Click to Confirm Download (Updated)",
                                    data=f,
                                    file_name=f"{selected}_Updated_Report.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.error(f"PDF Error: {e}")

# ==========================================
# TAB 3: TOOLS
# ==========================================
with tabs[2]:
    st.write("Agent Diagnostics Log")
    logs = st.session_state.agent.get_tool_calls()
    for log in reversed(logs):
        with st.expander(f"{log['tool']} - {time.ctime(log['timestamp'])}"):
            st.json(log)
import streamlit as st
import yaml

# Initialize page layout to wide screen for the side-by-side comparison
st.set_page_config(layout="wide")
st.title("🛡️ CISSP Token-Saver Chatbot Demo")
st.subheader("Hackathon Proof of Concept: YAML Schema vs. Raw PDF Text")

# 1. Define our two data structures based on Page 6 of the document
RAW_PDF_TEXT = """
Responsibilities of Key Roles
Role: Data Owner. Duties: Defines classification, approves access, sets retention, requests audits.
Role: Data Custodian. Duties: Maintains backups, configures ACLs, updates classification labels.
Role: System Owner. Duties: Oversees systems that store/process data, manages OS/application-level security.
Role: User. Duties: Uses data per policy, reports suspicious activity.
Role: Privacy Officer. Duties: Ensures data handling aligns with privacy laws and corporate policies.
Role: Compliance Officer. Duties: Audits classification policy adherence, especially in regulated sectors (e.g., finance, healthcare).
"""

YAML_DATA = """
cissp_roles:
  data_owner: [classify, approve_access, set_retention, request_audits]
  data_custodian: [backup, config_acls, update_labels]
  system_owner: [oversee_infrastructure, manage_os_app_security]
  user: [use_per_policy, report_anomalies]
  privacy_officer: [align_privacy_laws, enforce_privacy_policy]
  compliance_officer: [audit_policy_adherence, check_regulated_sectors]
"""

# Simple approximation function: 1 word/token placeholder roughly equals 4 characters for metrics display
def estimate_tokens(text):
    return len(text.split()) + int(len(text) * 0.1)

# 2. User Input Section
user_query = st.text_input("💬 Ask the CISSP Bot a role responsibility question:", 
                          value="Who configures access control lists?")

# Dummy response simulation for the demo frontend setup (Replace with actual OpenAI API calls if keys are provided)
def simulate_ai_response(prompt_type, query):
    if "access control" in query.lower() or "acls" in query.lower():
        if prompt_type == "raw":
            return "Based on the provided documentation, the role responsible for configuring access control lists (ACLs) is the Data Custodian, who also maintains backups and updates classification labels."
        return "data_custodian"
    return "Information not found in context."

if user_query:
    # Calculate metrics
    raw_tokens = estimate_tokens(RAW_PDF_TEXT + user_query)
    yaml_tokens = estimate_tokens(YAML_DATA + user_query)
    savings = ((raw_tokens - yaml_tokens) / raw_tokens) * 100

    # Display global metrics banner
    st.info(f"💡 **Token Reduction Impact:** Your YAML optimization project reduces input data size by **{savings:.1f}%** for this query!")

    # Create two layout columns
    col1, col2 = st.columns(2)

    with col1:
        st.error("❌ Approach A: Searching Raw PDF Document Context")
        st.metric(label="Estimated Input Tokens Passed", value=raw_tokens)
        
        with st.expander("View Payload Sent to LLM"):
            st.code(RAW_PDF_TEXT, language="text")
            
        ai_raw_response = simulate_ai_response("raw", user_query)
        st.markdown(f"**AI Response:** {ai_raw_response}")
        st.caption("⚠️ *Notice how the response includes extra conversational words, costing more output tokens.*")

    with col2:
        st.success("✅ Approach B: Querying Compressed YAML Schema Module")
        st.metric(label="Estimated Input Tokens Passed", value=yaml_tokens, delta=f"-{raw_tokens - yaml_tokens} tokens")
        
        with st.expander("View Payload Sent to LLM"):
            st.code(YAML_DATA, language="yaml")
            
        ai_yaml_response = simulate_ai_response("yaml", user_query)
        st.markdown(f"**AI Response:** `{ai_yaml_response}`")
        st.caption("🎯 *Notice how the structure forces a hyper-precise, cheap, single-word return payload.*")

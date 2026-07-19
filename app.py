import streamlit as st
import yaml

# Establish layout architecture
st.set_page_config(layout="wide")
st.title("🛡️ Dynamic LLM Audit Token-Saver Chatbot")
st.subheader("Hackathon Proof of Concept: Multi-Layered Auditing Framework")

# 1. Sidebar File Upload Interface
st.sidebar.header("📁 Step 1: Upload Your Data Sources")
uploaded_raw = st.sidebar.file_uploader("Upload Raw text file (.txt)", type=["txt"])
uploaded_yaml = st.sidebar.file_uploader("Upload Optimized YAML module (.yaml)", type=["yaml"])

# 2. Hardcoded fallback dataset based on the paper's framework
default_raw = """
Three-Layered LLM Auditing Framework:
1. Governance Audit: Audits technology providers, assessing internal workflows and quality management via white-box access.
2. Model Audit: Audits large language models after pre-training but prior to release, checking robustness and truthfulness via medium-level access.
3. Application Audit: Audits specific downstream applications, evaluating legal compliance and real-world user impact via black-box access.
"""

default_yaml = """
llm_auditing_framework:
  governance_audit: [technology_provider, workflows, white_box]
  model_audit: [large_language_model, robustness_truthfulness, medium_access]
  application_audit: [downstream_application, compliance_impact, black_box]
"""

# Extract text strings safely from upload pipelines
raw_context = uploaded_raw.read().decode("utf-8") if uploaded_raw else default_raw
yaml_context = uploaded_yaml.read().decode("utf-8") if uploaded_yaml else default_yaml

def estimate_tokens(text):
    return len(text.split()) + int(len(text) * 0.1)

# 3. Step 2: Search Query Input Area
user_query = st.text_input("💬 Ask the Bot a framework question:", 
                          value="What does a model audit look like?")

# 4. Parsing engine designed to find matching words
def dynamic_search(query, context, data_type):
    query_words = [w.lower() for w in query.replace("?", "").split() if len(w) > 3]
    
    if data_type == "yaml":
        try:
            parsed_yaml = yaml.safe_load(context)
            for key, val in parsed_yaml.items():
                if any(word in str(key).lower() for word in query_words):
                    return f"{key}: {val}"
                if isinstance(val, dict):
                    for subkey, subval in val.items():
                        if any(word in str(subkey).lower() for word in query_words):
                            return f"{subkey}: {subval}"
        except Exception:
            return "Error parsing YAML file structure."
        return "Key terms not matched in YAML layout structure."
    else:
        lines = context.split("\n")
        matched_lines = [line for line in lines if any(word in line.lower() for word in query_words)]
        if matched_lines:
            return " ".join(matched_lines[:2])
        return "No direct line matches found within the raw text document context."

# 5. Core Performance Matrix Render
if user_query:
    raw_tokens = estimate_tokens(raw_context + user_query)
    yaml_tokens = estimate_tokens(yaml_context + user_query)
    savings = max(0, ((raw_tokens - yaml_tokens) / raw_tokens) * 100)

    st.info(f"💡 **Token Reduction Impact:** Your setup shrinks input payload size by **{savings:.1f}%** dynamically!")

    col1, col2 = st.columns(2)

    with col1:
        st.error("❌ Approach A: Searching Raw Context Strings")
        st.metric(label="Estimated Input Tokens Passed", value=raw_tokens)
        with st.expander("Show Raw Data Payload"):
            st.code(raw_context, language="text")
        
        response_raw = dynamic_search(user_query, raw_context, "raw")
        st.markdown(f"**AI Search Output:** {response_raw}")

    with col2:
        st.success("✅ Approach B: Querying Compressed YAML Schema Mapping")
        st.metric(label="Estimated Input Tokens Passed", value=yaml_tokens, delta=f"-{max(0, raw_tokens - yaml_tokens)} tokens")
        with st.expander("Show Compressed YAML Payload"):
            st.code(yaml_context, language="yaml")
            
        response_yaml = dynamic_search(user_query, yaml_context, "yaml")
        st.markdown(f"**AI Search Output:** `{response_yaml}`")

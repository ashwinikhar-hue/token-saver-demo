import streamlit as st
import yaml

# Set wide page layout
st.set_page_config(layout="wide")
st.title("🛡️ Dynamic CISSP Token-Saver Chatbot")
st.subheader("Hackathon Proof of Concept: Real-Time YAML vs. Raw Document Search")

# 1. Sidebar File Upload Section
st.sidebar.header("📁 Step 1: Upload Your Data Sources")
uploaded_raw = st.sidebar.file_uploader("Upload Raw text file (.txt)", type=["txt"])
uploaded_yaml = st.sidebar.file_uploader("Upload Optimized YAML module (.yaml)", type=["yaml"])

# 2. Default data fallback if user hasn't uploaded anything yet
default_raw = "Responsibilities of Key Roles\nRole: Data Owner. Duties: Defines classification, approves access."
default_yaml = "cissp_roles:\n  data_owner: [classify, approve_access]"

raw_context = uploaded_raw.read().decode("utf-8") if uploaded_raw else default_raw
if uploaded_yaml:
    yaml_context = uploaded_yaml.read().decode("utf-8")
else:
    yaml_context = default_yaml

# Simple metrics helper
def estimate_tokens(text):
    return len(text.split()) + int(len(text) * 0.1)

# 3. Step 2: The User Search Query Interface
user_query = st.text_input("💬 Ask the CISSP Bot a question based on your data:", 
                          value="What are the duties of the data owner?")

# 4. Simple Rule-Based Dynamic Search Logic (Simulating RAG without heavy DB setup)
def dynamic_search(query, context, data_type):
    query_words = [w.lower() for w in query.replace("?", "").split() if len(w) > 3]
    
    if data_type == "yaml":
        try:
            parsed_yaml = yaml.safe_load(context)
            # Traverse YAML keys dynamically based on matching query words
            for key, val in parsed_yaml.items():
                if any(word in str(key).lower() for word in query_words):
                    return f"{key}: {val}"
                if isinstance(val, dict):
                    for subkey, subval in val.items():
                        if any(word in str(subkey).lower() for word in query_words):
                            return f"{subkey}: {subval}"
        except Exception:
            return "Error parsing YAML file structure."
        return "Key query terms not matched in YAML schema structure."
        
    else:
        # Simple line-by-line raw phrase finder
        lines = context.split("\n")
        matched_lines = [line for line in lines if any(word in line.lower() for word in query_words)]
        if matched_lines:
            return " ".join(matched_lines[:2])
        return "Context chunk not found in raw text document matching search terms."

# 5. Core Application Processing
if user_query:
    raw_tokens = estimate_tokens(raw_context + user_query)
    yaml_tokens = estimate_tokens(yaml_context + user_query)
    savings = max(0, ((raw_tokens - yaml_tokens) / raw_tokens) * 100)

    st.info(f"💡 **Token Reduction Impact:** Your structural setup reduces processed text size by **{savings:.1f}%** dynamically!")

    col1, col2 = st.columns(2)

    with col1:
        st.error("❌ Approach A: Searching Raw Unstructured Context")
        st.metric(label="Estimated Input Tokens Passed", value=raw_tokens)
        with st.expander("Show Raw Data Payload"):
            st.code(raw_context, language="text")
        
        response_raw = dynamic_search(user_query, raw_context, "raw")
        st.markdown(f"**AI Search Output:** {response_raw}")

    with col2:
        st.success("✅ Approach B: Querying Compressed YAML Schema")
        st.metric(label="Estimated Input Tokens Passed", value=yaml_tokens, delta=f"-{max(0, raw_tokens - yaml_tokens)} tokens")
        with st.expander("Show Compressed YAML Payload"):
            st.code(yaml_context, language="yaml")
            
        response_yaml = dynamic_search(user_query, yaml_context, "yaml")
        st.markdown(f"**AI Search Output:** `{response_yaml}`")

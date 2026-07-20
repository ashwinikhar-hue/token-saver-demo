import streamlit as st
import os
import yaml
from pypdf import PdfReader
from docx import Document

# Establish layout architecture
st.set_page_config(layout="wide")
st.title("🤖 Multi-Format Document-to-YAML Optimizer")
st.subheader("Hackathon Strategy: Automated Cross-Platform Data Structuring")

# Define target workspace configurations
SOURCE_DIR = "./source_docs"
CACHE_DIR = "./yaml_cache"

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def estimate_tokens(text):
    return len(text.split()) + int(len(text) * 0.1)

# -------------------------------------------------------------
# CORE EXTRACTOR ENGINE FOR MULTIPLE EXTENSIONS
# -------------------------------------------------------------
def extract_text_from_file(filepath, extension):
    text_content = ""
    try:
        if extension == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                text_content = f.read()
                
        elif extension == ".pdf":
            reader = PdfReader(filepath)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
                    
        elif extension == ".docx":
            doc = Document(filepath)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content += paragraph.text + "\n"
    except Exception as e:
        st.sidebar.error(f"Error reading {os.path.basename(filepath)}: {str(e)}")
        
    return text_content

# -------------------------------------------------------------
# STRUCTURED DATA PARSER CONVERSION LAYER
# -------------------------------------------------------------
def automatic_yaml_generator():
    files_processed = 0
    # Scan the local source_docs folder
    for filename in os.listdir(SOURCE_DIR):
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        if ext in [".txt", ".pdf", ".docx"]:
            filepath = os.path.join(SOURCE_DIR, filename)
            raw_text = extract_text_from_file(filepath, ext)
            
            if not raw_text.strip():
                continue
                
            # Rule-based chunk compiler mapping structural attributes into key-value data paths
            structured_map = {}
            lines = raw_text.split("\n")
            
            for index, line in enumerate(lines):
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                    
                # Case 1: Key-value formatting logic splits (e.g., Role: Data Owner)
                if ":" in cleaned_line:
                    parts = cleaned_line.split(":", 1)
                    key = parts[0].strip().lower().replace(" ", "_").replace("-", "_")
                    value = parts[1].strip()
                    # Strip out characters that break standard YAML markup parsing rules
                    key = "".join(c for c in key if c.isalnum() or c == "_")
                    if len(key) > 2 and len(value) > 4:
                        structured_map[key] = value
                
                # Case 2: Definition string extraction (captures 'is characterized by', 'refers to')
                elif "is characterized by" in cleaned_line.lower() or "refers to" in cleaned_line.lower() or "is a process" in cleaned_line.lower():
                    words = cleaned_line.split()
                    key = f"definition_{index}"
                    if len(words) > 2:
                        key = f"def_{words[0].lower()}_{words[1].lower()}"
                    key = "".join(c for c in key if c.isalnum() or c == "_")
                    structured_map[key] = cleaned_line

            # Robust fallback logic mapping raw paragraph strings safely into keys if text is unstructured
            if not structured_map:
                structured_map["document_title"] = name.replace(" ", "_").lower()
                structured_map["extracted_summary"] = raw_text.replace("\n", " ")[:200].strip() + "..."
                # Segment remaining content cleanly
                chunks = [raw_text[i:i+400].replace("\n", " ").strip() for i in range(0, min(len(raw_text), 2000), 400)]
                for i, chunk in enumerate(chunks):
                    structured_map[f"content_segment_{i+1}"] = chunk

            # Write out file onto local drive
            yaml_filename = f"{name}.yaml"
            yaml_filepath = os.path.join(CACHE_DIR, yaml_filename)
            with open(yaml_filepath, "w", encoding="utf-8") as yf:
                yaml.dump(structured_map, yf, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
            files_processed += 1
            
    return files_processed

# -------------------------------------------------------------
# APPLICATION DASHBOARD RENDER LAYER
# -------------------------------------------------------------
st.sidebar.header("⚙️ Local System Controls")
st.sidebar.markdown(f"**Source Docs Directory:** `{SOURCE_DIR}/`")
st.sidebar.markdown(f"**Cached YAML Target Folder:** `{CACHE_DIR}/`")

if st.sidebar.button("🔄 Auto-Scan Folder & Convert to YAML"):
    count = automatic_yaml_generator()
    if count > 0:
        st.sidebar.success(f"Processed {count} file targets (.txt, .pdf, .docx) into search caches!")
    else:
        st.sidebar.warning("No new compatible documents located in source folder directories.")

# Dynamically populate user selectors based on any detected files
available_files = [f for f in os.listdir(SOURCE_DIR) if os.path.splitext(f)[1].lower() in [".txt", ".pdf", ".docx"]]

if available_files:
    selected_file = st.selectbox("📂 Select file to perform lookup comparisons against:", available_files)
    name, ext = os.path.splitext(selected_file)
    
    # Read text dynamically from original native source file
    raw_context = extract_text_from_file(os.path.join(SOURCE_DIR, selected_file), ext.lower())
    
    # Fetch automatically mapped YAML conversion counterpart
    yaml_path = os.path.join(CACHE_DIR, f"{name}.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as yf:
            yaml_context = yf.read()
    else:
        yaml_context = "--- \nstatus: Please click the 'Auto-Scan' button on the sidebar to compile this asset."
else:
    raw_context = "Auditing: Auditing is characterized by an independent examination of an entity."
    yaml_context = "auditing:\n  definition: Independent examination of an entity."

user_query = st.text_input("💬 Type your question here:", value="What is Auditing?")

def search_engine(query, context, mode):
    query_words = [w.lower() for w in query.replace("?", "").split() if len(w) > 3]
    query_lower = query.lower()
    is_definition_query = "what is" in query_lower or "define" in query_lower
    
    if mode == "yaml":
        try:
            data = yaml.safe_load(context)
            if is_definition_query:
                for k, v in data.items():
                    if "def" in str(k).lower() or "audit" in str(k).lower():
                        return f"**{k}**: {v}"
            for k, v in data.items():
                if any(w in str(k).lower() for w in query_words):
                    return f"**{k}**: {v}"
        except:
            return "Parsing error encountered."
        return "No specific schema coordinates matched query variables."
    else:
        lines = context.split("\n")
        if is_definition_query:
            for line in lines:
                if "audit" in line.lower() and any(t in line.lower() for t in ["characterized by", "refers to", "process"]):
                    return line.strip()
        matches = [l for l in lines if any(w in l.lower() for w in query_words)]
        return matches[0] if matches else "No raw text variables intercepted matching key words."

if user_query:
    raw_tokens = estimate_tokens(raw_context + user_query)
    yaml_tokens = estimate_tokens(yaml_context + user_query)
    savings = max(0, ((raw_tokens - yaml_tokens) / raw_tokens) * 100)

    st.info(f"📈 **Token Budget Metrics:** YAML structured compiler yielded an optimization matrix reducing dataset size by **{savings:.1f}%**.")

    col1, col2 = st.columns(2)
    with col1:
        st.error("❌ Approach A: Processing Native Unstructured Data")
        st.metric("Total Tokens Transmitted", raw_tokens)
        with st.expander("Show Native Text Extract"):
            st.text(raw_context)
        st.markdown(f"**Search Result:** {search_engine(user_query, raw_context, 'raw')}")

    with col2:
        st.success("✅ Approach B: Querying Auto-Generated YAML Database Layer")
        st.metric("Total Tokens Transmitted", yaml_tokens, delta=f"-{max(0, raw_tokens - yaml_tokens)} tokens")
        with st.expander("Show Optimized YAML Layout"):
            st.code(yaml_context, language="yaml")
        st.markdown(f"**Search Result:** {search_engine(user_query, yaml_context, 'yaml')}")

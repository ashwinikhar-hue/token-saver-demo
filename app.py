import streamlit as st
import os
import yaml
from pypdf import PdfReader
from docx import Document
import Levenshtein

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
                elif any(t in cleaned_line.lower() for t in ["is characterized by", "refers to", "is a process", "defined as"]):
                    words = cleaned_line.split()
                    key = f"definition_{index}"
                    if len(words) > 2:
                        key = f"def_{words[0].lower()}_{words[1].lower()}"
                    key = "".join(c for c in key if c.isalnum() or c == "_")
                    structured_map[key] = cleaned_line

            # Robust fallback logic mapping raw paragraph strings safely into keys if text is unstructured
            if not structured_map:
                name_key = name.replace(" ", "_").lower()
                structured_map[f"{name_key}_summary"] = raw_text.replace("\n", " ")[:200].strip() + "..."
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
# ADVANCED DISTANCE-BASED SEARCH ENGINE
# -------------------------------------------------------------
def smart_search_engine(query, context, mode):
    query_clean = query.lower().strip().replace("?", "")
    query_words = set(w for w in query_clean.split() if len(w) > 3)
    
    if mode == "yaml":
        try:
            data = yaml.safe_load(context)
            if not data:
                return "Empty database container schema."
            
            best_key = None
            best_score = -1
            
            for k, v in data.items():
                k_clean = str(k).lower().replace("_", " ")
                # Strategy 1: Word intersection count overlap
                k_words = set(str(k).lower().split("_"))
                overlap = len(query_words.intersection(k_words))
                
                # Strategy 2: String similarity matching ratio
                similarity = Levenshtein.ratio(query_clean, k_clean)
                total_score = (overlap * 2) + similarity
                
                if total_score > best_score:
                    best_score = total_score
                    best_key = k
            
            if best_key and best_score > 0.3:
                return f"**{best_key}**: {data[best_key]}"
            return "No matching schema parameters located in the YAML index layer."
        except:
            return "Parsing error encountered reading data schema layout."
            
    else:
        lines = [line.strip() for line in context.split("\n") if line.strip()]
        if not lines:
            return "No raw context data extracted found."
            
        best_line = None
        best_score = -1
        
        for line in lines:
            line_clean = line.lower()
            line_words = set(line_clean.split())
            overlap = len(query_words.intersection(line_words))
            
            # Boost score if line explicitly mentions a common diagnostic definition indicator
            boost = 1.5 if any(t in line_clean for t in ["refers to", "characterized by", "is a"]) else 0
            total_score = overlap + boost
            
            if total_score > best_score:
                best_score = total_score
                best_line = line
                
        if best_line and best_score > 0:
            return best_line
        return "No text variables intercepted matching key words."

# -------------------------------------------------------------
# APPLICATION DASHBOARD RENDER LAYER
# -------------------------------------------------------------
st.sidebar.header("⚙️ Local System Controls")
st.sidebar.markdown(f"**Source Docs Directory:** `{SOURCE_DIR}/`")
st.sidebar.markdown(f"**Cached YAML Target Folder:** `{CACHE_DIR}/`")

if st.sidebar.button("🔄 Auto-Scan Folder & Convert to YAML"):
    count = automatic_yaml_generator()
    if count > 0:
        st.sidebar.success(f"Processed {count} file targets into search caches!")
        st.rerun()
    else:
        st.sidebar.warning("No new compatible documents located in source folder directories.")

# Dynamically populate user selectors based on any detected files
available_files = [f for f in os.listdir(SOURCE_DIR) if os.path.splitext(f).lower() in [".txt", ".pdf", ".docx"]]

if available_files:
    selected_file = st.selectbox("📂 Select file to perform lookup comparisons against:", available_files)
    name, ext = os.path.splitext(selected_file)
    
    raw_context = extract_text_from_file(os.path.join(SOURCE_DIR, selected_file), ext.lower())
    
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
        st.markdown(f"**Search Result:** {smart_search_engine(user_query, raw_context, 'raw')}")

    with col2:
        st.success("✅ Approach B: Querying Auto-Generated YAML Database Layer")
        st.metric("Total Tokens Transmitted", yaml_tokens, delta=f"-{max(0, raw_tokens - yaml_tokens)} tokens")
        with st.expander("Show Optimized YAML Layout"):

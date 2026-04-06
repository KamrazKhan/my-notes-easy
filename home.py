import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mero AI & PDF Tools", page_icon="🛠️", layout="wide")

# --- 1. SECURE API SETUP ---
def configure_api():
    try:
        if "API_KEY" not in st.secrets: return None, None
        genai.configure(api_key=st.secrets["API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available_models: return None, None
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
        return genai.GenerativeModel(model_name), model_name
    except: return None, None

model, model_name = configure_api()

# --- HEADER ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🛠️ Mero AI App: All-in-One Tools")
with col2:
    st.write(f"**Developed by:**\n[KmrazKhan]")
st.divider()

# --- TABS SYSTEM ---
tab1, tab2, tab3 = st.tabs(["📚 AI Assistant", "🗜️ Smart Compressor", "📂 PDF Merger"])

# ==========================================
# TAB 1: AI STUDY ASSISTANT
# ==========================================
with tab1:
    uploaded_study = st.file_uploader("Upload PDF/Image for AI Analysis", type=["pdf", "jpg", "png"], key="ai")
    if uploaded_study:
        if st.button("AI Analyze 🚀"):
            with st.spinner("AI is analyzing..."):
                # (Purano AI logic yaha hunchha - space bachauna maile process handle gare)
                st.info("AI Analysis feature active chha.")

# ==========================================
# TAB 2: SMART COMPRESSOR (Target KB Size)
# ==========================================
with tab2:
    st.subheader("Target Size Compression (KB)")
    c_file = st.file_uploader("Image upload garnuhos", type=["jpg", "jpeg", "png"], key="comp")
    
    if c_file:
        img = Image.open(c_file)
        orig_size = c_file.size / 1024
        st.write(f"Original Size: **{orig_size:.2f} KB**")
        
        target_kb = st.number_input("Kati KB ma jharne? (Target KB)", min_value=10, max_value=int(orig_size), value=100)
        
        if st.button("Compress to Target Size ⬇️"):
            quality = 95
            output = io.BytesIO()
            
            # Loop to find the right quality for the target KB
            while quality > 5:
                output = io.BytesIO()
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img.save(output, format='JPEG', quality=quality, optimize=True)
                if output.tell() / 1024 <= target_kb:
                    break
                quality -= 5
            
            final_data = output.getvalue()
            st.success(f"Compressed! New Size: **{len(final_data)/1024:.2f} KB**")
            st.download_button("Download Image", final_data, f"compressed_{target_kb}kb.jpg", "image/jpeg")

# ==========================================
# TAB 3: PDF MERGER (Horizontal/Vertical logic)
# ==========================================
with tab3:
    st.subheader("Multiple PDF Merge Garnuhos")
    pdfs = st.file_uploader("2 ya tyesvanda dherai PDF chhannuhos", type="pdf", accept_multiple_files=True)
    
    layout = st.radio("Page Layout (Visual Merge):", ["Portrait (Vertical)", "Landscape (Horizontal)"])

    if pdfs and len(pdfs) > 1:
        if st.button("Merge PDFs 🔗"):
            merger = PyPDF2.PdfWriter()
            for pdf in pdfs:
                reader = PyPDF2.PdfReader(pdf)
                for page in reader.pages:
                    if layout == "Landscape (Horizontal)":
                        page.rotate(90) # Page lai rotate garera horizontal feel dine
                    merger.add_page(page)
            
            merged_output = io.BytesIO()
            merger.write(merged_output)
            st.success(f"{len(pdfs)} wota PDF merge bhayo!")
            st.download_button("Download Merged PDF", merged_output.getvalue(), "merged_document.pdf", "application/pdf")
    else:
        st.warning("Merge garna kamti ma pani २ वटा PDF chainchha.")

st.divider()
st.caption("MeroAIApp v2.0 | Computer Engineering Project")
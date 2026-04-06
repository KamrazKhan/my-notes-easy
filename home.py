import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import io
import zipfile

# Naya library: PDF lai image ma badalna ko lagi
try:
    import fitz  # PyMuPDF
except ImportError:
    st.error("PyMuPDF library bhetiena! requirements.txt ma PyMuPDF thapnuhos.")

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
    st.markdown("<br>", unsafe_allow_html=True)
    st.write(f"**Developed by:**\nKamraj Kha Paithan")
    st.caption("Computer Engineering")
st.divider()

# --- TABS SYSTEM ---
tab1, tab2, tab3, tab4 = st.tabs(["📚 AI Assistant", "🗜️ Smart Compressor", "📂 Merge (PDF+Image)", "🖼️ PDF to Image"])

# ==========================================
# TAB 1: AI STUDY ASSISTANT
# ==========================================
with tab1:
    st.subheader("PDF ya Image lai Simple Bhasa ma bujhnuhos!")
    uploaded_study = st.file_uploader("Upload PDF/Image for AI Analysis", type=["pdf", "jpg", "png"], key="ai")
    
    if uploaded_study:
        ai_input = None
        if "pdf" in uploaded_study.type:
            pdf_reader = PyPDF2.PdfReader(uploaded_study)
            text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            ai_input = f"CONTEXT:\n{text[:15000]}"
        else:
            img = Image.open(uploaded_study)
            st.image(img, caption="Uploaded Image", use_container_width=True)
            ai_input = ["Explain this image simply in Hinglish.", img]

        task = st.radio("K garna chahanchhunu hunchha?", ["Simple Explanation (Hinglish)", "Short Summary", "Exam Questions"], key="ai_task")

        if st.button("AI Analyze 🚀"):
            if model:
                with st.spinner("AI is analyzing..."):
                    try:
                        prompts = {
                            "Simple Explanation (Hinglish)": "Explain this very simply like a friendly teacher in a mix of English and Nepali: ",
                            "Short Summary": "Provide a short bullet-point summary: ",
                            "Exam Questions": "Generate 5 important exam questions and answers: "
                        }
                        if isinstance(ai_input, str):
                            res = model.generate_content(prompts[task] + ai_input)
                        else:
                            res = model.generate_content([prompts[task] + ai_input[0], ai_input[1]])
                        st.markdown("### 💡 AI Result:")
                        st.write(res.text)
                    except Exception as e:
                        st.error(f"Generation Error: {e}")
            else:
                st.error("API Key configure bhayeko chhaina.")

# ==========================================
# TAB 2: SMART COMPRESSOR
# ==========================================
with tab2:
    st.subheader("Target Size Compression (KB)")
    c_file = st.file_uploader("Image upload garnuhos", type=["jpg", "jpeg", "png"], key="comp")
    if c_file:
        img = Image.open(c_file)
        orig_size = c_file.size / 1024
        st.write(f"Original Size: **{orig_size:.2f} KB**")
        target_kb = st.number_input("Kati KB ma jharne? (Target KB)", min_value=10, max_value=max(10, int(orig_size)), value=int(orig_size/2))
        
        if st.button("Compress to Target Size ⬇️"):
            quality, output = 95, io.BytesIO()
            while quality > 5:
                output = io.BytesIO()
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img.save(output, format='JPEG', quality=quality, optimize=True)
                if output.tell() / 1024 <= target_kb: break
                quality -= 5
            final_data = output.getvalue()
            st.success(f"Compressed! New Size: **{len(final_data)/1024:.2f} KB**")
            st.download_button("Download Image", final_data, f"compressed_{target_kb}kb.jpg", "image/jpeg")

# ==========================================
# TAB 3: MIXED MERGER (PDF & IMAGES)
# ==========================================
with tab3:
    st.subheader("PDF ra Images lai Eutai PDF ma Merge Garnuhos")
    st.info("💡 Timile PDF ko sath-sathai Photo haru (JPG, PNG) pani ekai choti select garna sakchau.")
    mix_files = st.file_uploader("Files chhannuhos", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True, key="merger")
    
    layout = st.radio("PDF Page Layout:", ["Portrait (Vertical)", "Landscape (Horizontal)"])

    if mix_files and len(mix_files) > 1:
        if st.button("Merge All Files 🔗"):
            merger = PyPDF2.PdfWriter()
            
            for file in mix_files:
                ext = file.name.split('.')[-1].lower()
                
                # Yadi file PDF ho bhane
                if ext == 'pdf':
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        if layout == "Landscape (Horizontal)": page.rotate(90)
                        merger.add_page(page)
                
                # Yadi file Image ho bhane (Image lai PDF page ma badalne)
                elif ext in ['jpg', 'jpeg', 'png']:
                    img = Image.open(file)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    # Image lai temporary PDF stream ma save garne
                    img_pdf_stream = io.BytesIO()
                    img.save(img_pdf_stream, format="PDF")
                    img_pdf_stream.seek(0) # Stream ko suru ma jane
                    
                    # Tyo temporary PDF lai read garera add garne
                    img_reader = PyPDF2.PdfReader(img_pdf_stream)
                    page = img_reader.pages[0]
                    if layout == "Landscape (Horizontal)": page.rotate(90)
                    merger.add_page(page)
            
            merged_output = io.BytesIO()
            merger.write(merged_output)
            st.success(f"{len(mix_files)} wota files merge bhayo!")
            st.download_button("Download Merged PDF", merged_output.getvalue(), "merged_document.pdf", "application/pdf")
    else:
        st.warning("Merge garna kamti ma pani २ वटा files (PDF/Image) chainchha.")

# ==========================================
# TAB 4: PDF TO IMAGE CONVERTER
# ==========================================
with tab4:
    st.subheader("PDF lai High-Quality Image ma badalnuhos")
    pdf_to_img_file = st.file_uploader("PDF upload garnuhos", type="pdf", key="p2i")
    
    if pdf_to_img_file:
        quality_option = st.selectbox("Image Quality/Size Chhannuhos:", ["Standard (1x)", "High Quality (2x)", "Ultra HD (3x)"])
        
        # Quality logic: Zoom matrix for PyMuPDF
        zoom_factor = 1
        if quality_option == "High Quality (2x)": zoom_factor = 2
        elif quality_option == "Ultra HD (3x)": zoom_factor = 3
        
        if st.button("Convert to Images 🖼️"):
            with st.spinner("Converting pages to images..."):
                try:
                    # PDF read garne
                    doc = fitz.open(stream=pdf_to_img_file.read(), filetype="pdf")
                    mat = fitz.Matrix(zoom_factor, zoom_factor) # Zoom matrix for quality
                    
                    # Dherai images hune bhayeko le Zip file banaune
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for page_num in range(len(doc)):
                            page = doc.load_page(page_num)
                            pix = page.get_pixmap(matrix=mat)
                            img_data = pix.tobytes("png")
                            # Zip file bhitra page halne
                            zip_file.writestr(f"Page_{page_num+1}.png", img_data)
                    
                    st.success(f"{len(doc)} pages converted successfully!")
                    
                    # Zip file download garna dine
                    st.download_button(
                        label="⬇️ Download All Images (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name=f"{pdf_to_img_file.name}_images.zip",
                        mime="application/zip"
                    )
                except Exception as e:
                    st.error(f"Conversion failed. Make sure PyMuPDF is installed. Error: {e}")

st.divider()
st.caption("MeroAIApp v3.0 | Computer Engineering Project")
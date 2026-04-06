import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import io # NAYA: Bytes ra files handle garna ko lagi

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Study Master", page_icon="📝", layout="wide")

# --- 1. SECURE API SETUP ---
def configure_api():
    try:
        if "API_KEY" not in st.secrets:
            st.error("Secrets.toml ma 'API_KEY' bhetiena!")
            return None, None
        
        genai.configure(api_key=st.secrets["API_KEY"])
        
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models: return None, None

        if 'models/gemini-1.5-flash' in available_models:
            selected_model_name = 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            selected_model_name = 'models/gemini-pro'
        else:
            selected_model_name = available_models[0]
            
        return genai.GenerativeModel(selected_model_name), selected_model_name

    except Exception as e:
        return None, None

model, model_name = configure_api()

# --- 2. HELPERS (PDF Read) ---
def extract_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content: text += content
    return text

# --- HEADER SECTION ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("📝 Mero AI App & Tools")
    if model_name: st.caption(f"Active AI Model: {model_name}")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("**Developed by:**")
    st.write("[KmrazKhan]")
    st.caption("Computer Engineering")
st.divider()

# --- APP TABS (UI LAYOUT) ---
# NAYA: App lai dui bhag ma baadhne
tab1, tab2 = st.tabs(["📚 AI Study Assistant", "🗜️ File Compressor (Size Reducer)"])

# ==========================================
# TAB 1: AI STUDY ASSISTANT (Timro Purano Code)
# ==========================================
with tab1:
    st.subheader("PDF ya Image lai Simple Bhasa ma bujhnuhos!")
    uploaded_study_file = st.file_uploader("Study ko lagi file chhannuhos", type=["pdf", "jpg", "jpeg", "png"], key="study_uploader")

    if uploaded_study_file is not None:
        file_type = uploaded_study_file.type
        ai_input = None
        content_ready = False

        if "pdf" in file_type:
            with st.status("Reading PDF..."):
                extracted_text = extract_pdf_text(uploaded_study_file)
                if extracted_text:
                    ai_input = f"CONTEXT:\n{extracted_text[:15000]}"
                    content_ready = True
        else:
            img = Image.open(uploaded_study_file)
            st.image(img, caption="Uploaded Image", use_container_width=True)
            ai_input = ["Explain this image simply in Hinglish.", img]
            content_ready = True

        if content_ready:
            task = st.radio("K garna chahanchhunu hunchha?", 
                            ["Simple Explanation (Hinglish)", "Short Summary", "Exam Questions"], key="ai_task")

            if st.button("Analyze with AI 🚀"):
                with st.spinner("AI is thinking..."):
                    try:
                        prompts = {
                            "Simple Explanation (Hinglish)": "Explain this very simply like a friendly teacher in a mix of English and Nepali. Use analogies: ",
                            "Short Summary": "Provide a short bullet-point summary: ",
                            "Exam Questions": "Generate 5 important exam questions and answers: "
                        }
                        final_prompt = prompts[task]
                        
                        if isinstance(ai_input, str):
                            response = model.generate_content(final_prompt + ai_input)
                        else:
                            response = model.generate_content([final_prompt + ai_input[0], ai_input[1]])
                        
                        st.subheader("💡 AI Result:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Generation Error: {e}")

# ==========================================
# TAB 2: FILE COMPRESSOR (Naya Feature)
# ==========================================
with tab2:
    st.subheader("Image ra PDF ko File Size ghataunuhos")
    compress_file = st.file_uploader("Compress garna file halnuhos", type=["pdf", "jpg", "jpeg", "png"], key="compress_uploader")
    
    if compress_file is not None:
        file_extension = compress_file.name.split('.')[-1].lower()
        
        # --- IMAGE COMPRESSION LOGIC ---
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(compress_file)
            st.image(img, caption=f"Original Image ({compress_file.size / 1024:.2f} KB)", width=300)
            
            # User le quality chhanne slider
            quality = st.slider("Compression Quality (10 Sabai vanda low, 90 High)", min_value=10, max_value=90, value=50)
            
            if st.button("Compress Image 🗜️"):
                # Convert to RGB if it's PNG to save as JPEG
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                
                # Image lai memory ma save garne
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', optimize=True, quality=quality)
                img_byte_arr = img_byte_arr.getvalue()
                
                st.success("Image successfully compressed!")
                
                # Download Button
                st.download_button(
                    label="⬇️ Download Compressed Image",
                    data=img_byte_arr,
                    file_name=f"compressed_{compress_file.name.split('.')[0]}.jpg",
                    mime="image/jpeg"
                )
                
        # --- PDF COMPRESSION LOGIC ---
        elif file_extension == 'pdf':
            st.write(f"Original PDF Size: **{compress_file.size / 1024:.2f} KB**")
            
            if st.button("Compress PDF 🗜️"):
                try:
                    reader = PyPDF2.PdfReader(compress_file)
                    writer = PyPDF2.PdfWriter()
                    
                    for page in reader.pages:
                        page.compress_content_streams() # PyPDF2 ko basic compression
                        writer.add_page(page)
                        
                    pdf_bytes = io.BytesIO()
                    writer.write(pdf_bytes)
                    compressed_pdf = pdf_bytes.getvalue()
                    
                    st.success("PDF compressed! (Note: Text PDF ma matra size dherai ghatxa)")
                    st.download_button(
                        label="⬇️ Download Compressed PDF",
                        data=compressed_pdf,
                        file_name=f"compressed_{compress_file.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF compress garda error aayo: {e}")

st.divider()
st.caption("Developed by a Computer Engineering Student | 2026")
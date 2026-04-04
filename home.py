import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Study Master", page_icon="📝", layout="centered")

# --- 1. SECURE API SETUP ---
def configure_api():
    try:
        # Check Streamlit Secrets
        if "API_KEY" not in st.secrets:
            st.error("Error: 'API_KEY' not found in Secrets! Please add it to secrets.toml or Cloud settings.")
            return None
        
        genai.configure(api_key=st.secrets["API_KEY"])
        
        # Model Selection Logic
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model
        except Exception:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        return None

model = configure_api()

# --- 2. HELPERS ---
def extract_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content: text += content
    return text

# --- 3. UI DESIGN ---
st.title("📝 AI Study Master (Nepal)")
st.subheader("PDF ya Image upload garnuhos ra simple bhasa ma bujhnuhos!")
st.divider()

# File Uploader for both PDF and Images
uploaded_file = st.file_uploader("File chhannuhos (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    content_ready = False
    ai_input = None

    # Processing PDF
    if "pdf" in file_type:
        with st.status("Reading PDF..."):
            extracted_text = extract_pdf_text(uploaded_file)
            if extracted_text:
                ai_input = f"CONTEXT FROM PDF:\n{extracted_text[:15000]}"
                content_ready = True
                st.success("PDF processed!")

    # Processing Image
    else:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_container_width=True)
        ai_input = [
            "Explain the content of this image in very simple language. If there is text, summarize it. Use Hinglish.",
            img
        ]
        content_ready = True

    if content_ready:
        st.divider()
        task = st.radio("K garna chahanchhunu hunchha?", 
                        ["Simple Explanation (Hinglish)", "Short Summary", "Exam Questions (QA)"])

        if st.button("Analyze with AI 🚀"):
            if model:
                with st.spinner("AI le sochdai chha..."):
                    try:
                        # Define final prompt based on task
                        if task == "Simple Explanation (Hinglish)":
                            prompt_prefix = "Explain this very simply like a friendly teacher using English and Nepali mix (Hinglish). Use analogies: "
                        elif task == "Short Summary":
                            prompt_prefix = "Provide a very short bullet-point summary of this: "
                        else:
                            prompt_prefix = "Generate 5 important exam questions and answers from this: "

                        # If it's a PDF (Text only)
                        if isinstance(ai_input, str):
                            response = model.generate_content(prompt_prefix + ai_input)
                        # If it's an Image (Multimodal)
                        else:
                            response = model.generate_content([prompt_prefix + ai_input[0], ai_input[1]])
                        
                        st.markdown("### 💡 AI Output:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"AI Error: {e}")
            else:
                st.error("API Model not ready. Key check garnuhos.")

st.divider()
st.caption("Developed for Computer Engineering Students | 2026")
# --- 3. UI DESIGN (Top Section with Developed By) ---
# Column 1 le 3 bhag ra Column 2 le 1 bhag space lincha (Total 4)
col1, col2 = st.columns([3, 1])

with col1:
    st.title("📝 AI Study Master")

with col2:
    # Right side ma padding thapera text lai mathi milaune
    st.markdown("<br>", unsafe_allow_html=True) # Sano space ko lagi
    st.write(f"**Developed by:** \n [KmrazKhan]") 
    st.caption("Computer Engineering")

st.subheader("PDF ya Image upload garnuhos ra simple bhasa ma bujhnuhos!")
st.divider()
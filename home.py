import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Study Master", page_icon="📝", layout="wide")

# --- 1. SECURE API SETUP (WITH AUTO-MODEL FINDER) ---
def configure_api():
    try:
        if "API_KEY" not in st.secrets:
            st.error("Secrets.toml ma 'API_KEY' bhetiena!")
            return None, None
        
        genai.configure(api_key=st.secrets["API_KEY"])
        
        # --- THE LOOP MODE: Available Model Khojne ---
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            st.error("Kunei pani compatible AI model bhetiena.")
            return None, None

        # Priority List: Paila Flash, ani Pro, ani aru
        selected_model_name = ""
        if 'models/gemini-1.5-flash' in available_models:
            selected_model_name = 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            selected_model_name = 'models/gemini-pro'
        else:
            selected_model_name = available_models[0] # J bhetinchha tyahi line
            
        return genai.GenerativeModel(selected_model_name), selected_model_name

    except Exception as e:
        st.error(f"Configuration Error: {e}")
        return None, None

# Initialize Model
model, model_name = configure_api()

# --- 2. HELPERS ---
def extract_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content: text += content
    return text

# --- 3. UI DESIGN ---
col1, col2 = st.columns([4, 1])

with col1:
    st.title("📝 AI Study Master")
    if model_name:
        st.caption(f"Active AI Model: {model_name}")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("**Developed by:**")
    st.write("[KmrazKhan]")
    st.caption("Computer Engineering")

st.divider()
st.header("COMPLEX लाई Simple भासा मा बुझौ")
st.subheader("PDF ya Image upload garnuhos ra simple bhasa ma bujhnuhos!")
# File Uploader
uploaded_file = st.file_uploader("PDF ya Image upload garnuhos", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    ai_input = None
    content_ready = False

    if "pdf" in file_type:
        with st.status("Reading PDF..."):
            extracted_text = extract_pdf_text(uploaded_file)
            if extracted_text:
                ai_input = f"CONTEXT:\n{extracted_text[:15000]}"
                content_ready = True
    else:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_container_width=True)
        ai_input = ["Explain this image simply in Hinglish.", img]
        content_ready = True

    if content_ready:
        task = st.radio("K garna chahanchhunu hunchha?", 
                        ["Simple Explanation (Hinglish)", "Short Summary", "Exam Questions"])

        if st.button("Analyze with AI 🚀"):
            with st.spinner("AI is thinking..."):
                try:
                    # Prompts
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

st.divider()
st.caption("Developed by a Computer Engineering Student | 2026")


st.divider()
st.caption("Developed for engineering Students | 2026")
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
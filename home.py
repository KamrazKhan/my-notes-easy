import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- SECURE API SETUP ---
# Code ma key narakhnu, Secrets bata tanne
try:
    genai.configure(api_key=st.secrets["API_KEY"])
except Exception as e:
    st.error("API Key bhetena! Please check your Secrets settings.")

st.set_page_config(page_title="AI PDF Professor", page_icon="🎓", layout="wide")

st.title("🎓 Smart PDF Professor")
st.write("Aafno College ko PDF notes haru lai simple language ma bujhnuhos.")

# PDF text nikaalne function
def get_pdf_text(pdf_docs):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# UI Layout
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("PDF Upload Garnuhos", type="pdf")
    
if uploaded_file:
    # 1. Text extract garne
    raw_text = get_pdf_text(uploaded_file)
    
    # 2. Options selection
    st.info("PDF read vayo! Aba k garna chahanchhunu hunchha?")
    task = st.selectbox("Action chhannuhos:", 
                        ["Summary (Main Points)", 
                         "Explain Simply (Saral Bhasa)", 
                         "Generate 5 Questions (Exam Prep)"])

    if st.button("Start AI Process 🚀"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # --- IMPROVED PROMPT ENGINEERING ---
            if task == "Summary (Main Points)":
                prompt = f"Read this text and provide a high-level summary. Use bullet points for key concepts: \n\n {raw_text[:10000]}"
            
            elif task == "Explain Simply (Saral Bhasa)":
                prompt = f"Explain the core concepts of this text in very simple language. Use analogies and avoid technical jargon. Use a mix of English and Nepali (Hinglish) for better understanding. Explain like I am 12 years old: \n\n {raw_text[:10000]}"
            
            else:
                prompt = f"Based on this text, generate 5 important exam questions with short answers: \n\n {raw_text[:10000]}"

            with st.spinner("AI le analyze gardai chha..."):
                response = model.generate_content(prompt)
                st.subheader("AI Result:")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.warning("Paila side bata PDF upload garnuhos.")
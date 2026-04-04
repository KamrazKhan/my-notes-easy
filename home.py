import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI PDF Professor | Nepal",
    page_icon="🎓",
    layout="centered"
)

# --- 1. SECURE API SETUP ---
def configure_api():
    try:
        # Streamlit Secrets bata API Key tanne
        api_key = st.secrets["API_KEY"]
        genai.configure(api_key=api_key)
        
        # Best model automatically select garne logic
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Test run to check if model exists
            model.generate_content("test") 
            return model
        except Exception:
            # Yadi flash bhetena bhane available model khojne
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
    except Exception as e:
        st.error("API Key Configuration Error! Check your Secrets.toml or Streamlit Cloud Secrets.")
        return None

model = configure_api()

# --- 2. PDF PROCESSING FUNCTION ---
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        combined_text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                combined_text += content
        return combined_text
    except Exception as e:
        st.error(f"PDF read garna sakiyena: {e}")
        return ""

# --- 3. USER INTERFACE (UI) ---
st.title("🎓 Smart PDF Professor")
st.markdown("### Technical Notes lai Simple Bhasa ma Bujhnuhos")
st.divider()

# File Uploader
uploaded_file = st.file_uploader("Aafno College ko PDF (Notes) Upload garnuhos", type="pdf")

if uploaded_file is not None:
    with st.status("Processing your PDF...", expanded=True) as status:
        st.write("Reading text from PDF...")
        text_content = extract_text_from_pdf(uploaded_file)
        
        if text_content:
            st.write("Text extracted successfully!")
            status.update(label="PDF Ready!", state="complete", expanded=False)
            
            # Options for the user
            option = st.radio(
                "AI le k garos?",
                ["Summary (Important Points)", "Explain Simply (Easy Language)", "Generate Exam Questions"],
                index=1
            )

            if st.button("AI lai Kaam Lagau 🚀"):
                if model:
                    # PROMPT ENGINEERING
                    if option == "Summary (Important Points)":
                        user_prompt = f"Summarize the following text in clear bullet points focusing on main concepts:\n\n{text_content[:15000]}"
                    elif option == "Explain Simply (Easy Language)":
                        user_prompt = f"Explain this technical text in very simple words as if teaching a beginner. Use a mix of English and Nepali (Hinglish). Use real-life analogies:\n\n{text_content[:15000]}"
                    else:
                        user_prompt = f"Create 5 important exam questions and their short answers based on this text:\n\n{text_content[:15000]}"

                    with st.spinner("AI is thinking..."):
                        try:
                            response = model.generate_content(user_prompt)
                            st.subheader("💡 AI Professor says:")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"AI Generation Error: {e}")
                else:
                    st.error("Model initialize bhayena. API Key check garnuhos.")
        else:
            st.error("PDF bata text nikaalna sakiyena. File check garnuhos.")

# --- FOOTER ---
st.divider()
st.caption("Developed by a Computer Engineering Student | Powered by Gemini AI")
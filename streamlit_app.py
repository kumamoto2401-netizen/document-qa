import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide your Gemini API key. "
)

# Ask user for their Gemini API key via `st.text_input`.
# You may also store the API key in `./.streamlit/secrets.toml` using the key name "gemini_api_key".
gemini_api_key = st.secrets.get("gemini_api_key")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # NOTE: There is no official OpenAI Python client for Gemini. 
    # You need to use Google's generativeai client or an HTTP client for Gemini API.
    # For demonstration, we'll show a typical approach using google.generativeai
    # (You must install google-generativeai: pip install google-generativeai)
    import google.generativeai as genai

    genai.configure(api_key=gemini_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        document = uploaded_file.read().decode(errors="ignore")
        prompt = f"Here's a document: {document} \n\n---\n\n {question}"

        # Call Gemini 1.5 Flash (gemini-1.5-flash)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        # Streaming is not directly supported in google-generativeai as of now,
        # so we display the result after retrieval.
        response = model.generate_content(prompt)
        st.write(response.text)

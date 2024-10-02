from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import google.generativeai as genai

# Configure the Google Generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load the Gemini model and get a response
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    """Get response from Gemini model."""
    response = chat.send_message(question, stream=True)
    return response

# Initialize the Streamlit app
st.set_page_config(page_title="Q&A Demo")
st.header("Gemini LLM Application")

# Google Sign-In button
if st.button("Sign in with Google"):
    # Redirect the user to the Google Sign-In page
    auth_url = "https://accounts.google.com/o/oauth2/auth"
    client_id = os.getenv("65938622292-1koifr5suake794g6htbq6en3vh3mrs0.apps.googleusercontent.com")  # Use environment variable for client ID
    redirect_uri = "http://localhost:8501/"  # Replace with your redirect URI
    scope = "openid"  # Replace with the desired scopes
    state = "state123"  # Replace with a unique state value
    auth_endpoint = f"{auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"
    st.markdown(f'<a href="{auth_endpoint}">Click here to sign in with Google</a>', unsafe_allow_html=True)

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# User input for questions
input = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

if submit and input:
    response = get_gemini_response(input)
    # Add user query and response to session chat history
    st.session_state['chat_history'].append(("You", input))
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot", chunk.text))

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")

def get_google_id_token(auth_code, client_id):
    """Fetch the Google ID token using the authorization code."""
    try:
        token = id_token.fetch_id_token(requests.Request(), auth_code, client_id)
        return token
    except ValueError as e:
        st.error(f"Error retrieving ID token: {e}")

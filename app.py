import streamlit as st
from requests_oauthlib import OAuth2Session
import google.generativeai as genai
import secrets

# OAuth 2.0 Configuration
CLIENT_ID = st.secrets["google"]["client_id"]
CLIENT_SECRET = st.secrets["google"]["client_secret"]
AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
SCOPE = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]
REDIRECT_URI = 'http://localhost:8501'

# Initialize OAuth2 session
oauth = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)

# Function to get user info
def get_user_info(token):
    oauth.token = token
    response = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
    return response.json()

# Initialize the Streamlit app
st.set_page_config(page_title="Chat with Gemini")
st.header("Chat with Gemini LLM")

# Authentication Logic
if 'oauth_token' not in st.session_state:
    if 'code' not in st.query_params:
        # User is not authenticated; show login link
        authorization_url, _ = oauth.authorization_url(AUTHORIZATION_BASE_URL, access_type="offline", prompt="select_account")
        st.markdown(f'[Login with Google]({authorization_url})')
    else:
        # User has returned with a code
        code = st.query_params['code']
        st.write(f"Authorization Code: {code}")  # Log the code for debugging

        try:
            # Fetch the access token
            token = oauth.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, code=code)
            st.session_state['oauth_token'] = token
            
            # Get user info
            user_info = get_user_info(token)
            st.session_state['user_info'] = user_info  # Store user info
            st.rerun()  # Rerun to refresh the app state
        except Exception as e:
            st.error(f"Error fetching token: {str(e)}")
else:
    # User is authenticated
    user_info = st.session_state['user_info']
    st.write(f"Logged in as: {user_info['email']}")  # Display user's email

    # Configure the Google Generative AI API key using Streamlit secrets
    genai.configure(api_key=st.secrets["google"]["api_key"])  # Ensure your API key is added to Streamlit secrets

    # Chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Initialize the Generative Model
    model = genai.GenerativeModel("tunedModels/calm-mifnbptbnaep")  # Use your fine-tuned model name
    chat = model.start_chat(history=[])

    # Function to get a response from the model
    def get_response(question):
        """Get response from the model."""
        response = chat.send_message(question)
        return response.text  # Access the response text

    # User input for questions
    user_input = st.text_input("Ask a question:")
    submit = st.button("Send")

    if submit and user_input:
        response_text = get_response(user_input)
        # Add user query and response to session chat history
        st.session_state['chat_history'].append(("You", user_input))
        st.session_state['chat_history'].append(("Bot", response_text))

    # Display chat history
    st.subheader("Chat History")
    for role, text in st.session_state['chat_history']:
        st.write(f"{role}: {text}")

    # Logout button to clear chat history
    if st.button("Logout"):
        st.session_state.pop('oauth_token', None)
        st.session_state.pop('user_info', None)
        st.session_state.pop('chat_history', None)
        st.experimental_rerun()

# Debugging Output
st.write("Current Session State:", st.session_state)

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Google OAuth Credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"

# OAuth2 Session
client = OAuth2Session(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    scope="openid email profile",
    redirect_uri=REDIRECT_URI
)

def authenticate_user():
    """Handles Google OAuth login and returns user info."""
    
    if "user" in st.session_state:
        return st.session_state["user"]

    query_params = st.query_params
    if "code" in query_params:
        try:
            # Fetch the access token
            token = client.fetch_token(
                "https://oauth2.googleapis.com/token",
                grant_type="authorization_code",
                code=query_params["code"],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                redirect_uri=REDIRECT_URI
            )

            # Store the token properly
            st.session_state["access_token"] = token["access_token"]

            # Fetch user info using the token
            user_info = client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
            ).json()

            # Store user info in session state
            st.session_state["user"] = user_info
            st.rerun()  

        except Exception as e:
            st.error(f"Authentication failed: {e}")
            return None

    # Generate login URL
    auth_url, state = client.create_authorization_url("https://accounts.google.com/o/oauth2/auth")
    
    st.title("📄 Multi User Chatbot")
    st.markdown(f'<a href="{auth_url}" target="_self"><button>Login with Google</button></a>', unsafe_allow_html=True)
    
    return None  

def logout_user():
    """Logout user by revoking their access token"""
    access_token = st.session_state.get("access_token")

    if access_token:
        revoke_url = "https://oauth2.googleapis.com/revoke"
        response = requests.post(
            revoke_url,
            params={"token": access_token},  # Google requires token as URL parameter
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
# Handle expired/revoked token error
        if response.status_code == 200:
            st.session_state.clear()  # Clear session data
        elif response.status_code == 400 and "invalid_token" in response.text:
            st.warning("Session expired. Logging you out...")
            st.session_state.clear()  # Clear session even if token is invalid
        else:
            st.error(f"Logout failed: {response.json()}")  # Show detailed error

    else:
        st.warning("No active session found.")

    # Clear query parameters
    st.query_params.clear()

    # Refresh the page
    st.rerun()

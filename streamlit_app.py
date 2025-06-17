# streamlit_app.py - Streamlit Frontend Application (Key argument removed from form_submit_button)

import streamlit as st
import requests

# --- Configuration ---
FASTAPI_BASE_URL = "http://127.0.0.1:8000"

# --- Helper Functions for API Calls ---

def register_user_api(username, password):
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/register",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error connecting to backend or invalid response: {e}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

def login_user_api(username, password):
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/token",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error connecting to backend or invalid response: {e}"
    except Exception as e:
        return None, f"An unexpected error occurred: e"

def get_current_user_api(token):
    try:
        response = requests.get(
            f"{FASTAPI_BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error connecting to backend or invalid response: e"
    except Exception as e:
        return None, f"An unexpected error occurred: e"

def generate_api_key_api(token):
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/users/me/generate-api-key",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error connecting to backend or invalid response: e"
    except Exception as e:
        return None, f"An unexpected error occurred: e"

def get_protected_data_api(api_key):
    try:
        response = requests.get(
            f"{FASTAPI_BASE_URL}/api-key-protected",
            headers={"X-API-Key": api_key}
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error connecting to backend or invalid response: e"
    except Exception as e:
        return None, f"An unexpected error occurred: e"

# --- Streamlit UI Setup ---

st.set_page_config(page_title="FastAPI + Streamlit Auth", layout="centered")

st.title("User Authentication & API Key System")

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "generated_api_key" not in st.session_state:
    st.session_state.generated_api_key = None

# --- Main Application Logic ---

if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.username}!")

    st.subheader("Your Profile (Authenticated via JWT)")
    if st.button("Refresh Profile (using JWT)", key="refresh_profile_jwt"):
        user_info, error = get_current_user_api(st.session_state.access_token)
        if user_info:
            st.write(f"Username: {user_info['username']}")
        else:
            st.error(f"Failed to fetch profile: {error}. Your session might have expired. Please log in again.")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.access_token = None
            st.rerun()

    st.subheader("Generate & Use API Key")

    if st.session_state.generated_api_key:
        st.info("Your API Key (keep it secret and do not share!):")
        st.code(st.session_state.generated_api_key)

        if st.button("Copy API Key to Clipboard", key="copy_api_key"):
            st.components.v1.html(f"""
            <script>
            function copyTextToClipboard(text) {{
                if (!navigator.clipboard) {{
                    fallbackCopyTextToClipboard(text);
                    return;
                }}
                navigator.clipboard.writeText(text).then(function() {{
                }}, function(err) {{
                }});
            }}

            function fallbackCopyTextToClipboard(text) {{
                var textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                textArea.style.top = "0";
                textArea.style.left = "0";
                textArea.style.width = "2em";
                textArea.style.height = "2em";
                textArea.style.padding = "0";
                textArea.style.border = "none";
                textArea.style.outline = "none";
                textArea.style.boxShadow = "none";
                textArea.style.background = "transparent";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {{
                    var successful = document.execCommand('copy');
                }} catch (err) {{
                }}
                document.body.removeChild(textArea);
            }}
            copyTextToClipboard("{st.session_state.generated_api_key}");
            </script>
            """, height=0, width=0)
            st.success("API Key copied to clipboard!")
    else:
        st.warning("No API Key generated yet for this session. Click 'Generate' below.")

    if st.button("Generate New API Key", key="generate_api_key"):
        st.info("Generating a new API Key... This will invalidate any old keys for this user.")
        api_key_data, error = generate_api_key_api(st.session_state.access_token)
        if api_key_data:
            st.session_state.generated_api_key = api_key_data["key_value"]
            st.success("API Key generated successfully!")
            st.rerun()
        else:
            st.error(f"Failed to generate API Key: {error}")

    if st.session_state.generated_api_key:
        st.markdown("---")
        st.subheader("Test API Key Protected Endpoint")
        st.write("Click the button below to access data using your generated API Key.")
        if st.button("Access Protected Data (using API Key)", key="test_api_key_button"):
            st.info("Attempting to access protected data using the API Key...")
            protected_data, error = get_protected_data_api(st.session_state.generated_api_key)
            if protected_data:
                st.success("Successfully accessed protected data!")
                st.json(protected_data)
            else:
                st.error(f"Failed to access protected data: {error}")
                st.warning("This could be due to an invalid/expired key, or the backend is not running. Try generating a new key or checking the backend server.")

    st.markdown("---")
    if st.button("Logout", help="Click to log out of your session", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.access_token = None
        st.session_state.generated_api_key = None
        st.info("You have been logged out.")
        st.rerun()

else:
    st.subheader("Login or Register to Continue")

    choice = st.radio("Choose an action", ["Login", "Register"], key="auth_choice")

    with st.form("auth_form"):
        input_username = st.text_input("Username", key="input_username")
        input_password = st.text_input("Password", type="password", key="input_password")
        # THIS IS THE LINE THAT WAS CHANGED: 'key' argument removed from form_submit_button
        submitted = st.form_submit_button("Submit")

        if submitted:
            if choice == "Register":
                if not input_username or not input_password:
                    st.warning("Please enter both username and password.")
                else:
                    st.info("Attempting to register...")
                    user_data, error = register_user_api(input_username, input_password)
                    if user_data:
                        st.success(f"User '{user_data['username']}' registered successfully! You can now log in.")
                    else:
                        st.error(f"Registration failed: {error}")

            elif choice == "Login":
                if not input_username or not input_password:
                    st.warning("Please enter both username and password.")
                else:
                    st.info("Attempting to log in...")
                    token_data, error = login_user_api(input_username, input_password)
                    if token_data:
                        st.session_state.access_token = token_data["access_token"]
                        user_info, user_error = get_current_user_api(st.session_state.access_token)
                        if user_info:
                            st.session_state.logged_in = True
                            st.session_state.username = user_info["username"]
                            st.success(f"Logged in as {st.session_state.username}!")
                            st.rerun()
                        else:
                            st.error(f"Login successful, but failed to retrieve user info: {user_error}. Please try again.")
                            st.session_state.access_token = None
                    else:
                        st.error(f"Login failed: {error}")

# --- Instructions Section ---
st.markdown("---")
st.markdown(
    """
    ### How to Run This Application:

    1.  **Open two separate terminal/command prompt windows.**

    2.  **In the FIRST Terminal (for FastAPI Backend):**
        * Navigate to the directory where you saved `main.py`:
            ```bash
            cd C:\\Users\\ADMIN\\Documents
            ```
        * Run the FastAPI backend:
            ```bash
            uvicorn main:app --reload
            ```
        * **CRITICAL:** Wait until you see `INFO: Application startup complete.` in this terminal. **Keep this terminal window open and active.**
        * **Optional Test:** Open your web browser and go to `http://127.0.0.1:8000/docs`. You should see the interactive FastAPI documentation. If you get a connection error here, troubleshoot your firewall or ensure the backend is truly running.

    3.  **In the SECOND Terminal (for Streamlit Frontend):**
        * Navigate to the same directory:
            ```bash
            cd C:\\Users\\ADMIN\\Documents
            ```
        * Run the Streamlit application:
            ```bash
            streamlit run streamlit_app.py
            ```
        * This should open a new tab in your web browser displaying the Streamlit app.

    ### **Usage:**

    * **Register:** Use the "Register" tab to create a new username and password.
    * **Login:** Switch to the "Login" tab and use your new credentials to log in.
    * **Generate API Key:** Once logged in, click "Generate New API Key". The key will be displayed.
    * **Test API Key:** Click "Access Protected Data (using API Key)" to see it working.
    """
)

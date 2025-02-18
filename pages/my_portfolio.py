import streamlit as st
import hashlib
import pandas as pd

# Set page config at the very beginning
st.set_page_config(page_title="Login", layout="wide")

# Simulating a simple database of users (username and hashed passwords)
users_db = {}

# Simulating a table with some data to display after login
data_table = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [24, 30, 29],
    "City": ["New York", "Los Angeles", "Chicago"]
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Check if user is already logged in (session state)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Show login or register UI if not logged in
if not st.session_state.logged_in:
    st.title("Login / Register")
    
    # Sidebar for selecting login or register
    mode = st.sidebar.radio("Choose an action", ("Login", "Create Account"))

    if mode == "Login":
        st.subheader("Login to your account")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users_db and verify_password(users_db[username], password):
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.rerun()  # Re-run the app to show the table

            else:
                st.error("Invalid username or password")

    elif mode == "Create Account":
        st.subheader("Create a new account")

        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        confirm_password = st.text_input("Confirm your password", type="password")

        if st.button("Create Account"):
            if new_username in users_db:
                st.error("Username already exists. Please choose a different username.")
            elif new_password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                users_db[new_username] = hash_password(new_password)
                st.session_state.logged_in = True
                st.success("Account created successfully! You are now logged in.")
                st.rerun()  # Re-run the app to show the table
else:
    # If logged in, display the data table
    st.title("Welcome! Here is your data table:")

    df = pd.DataFrame(data_table)
    st.dataframe(df)

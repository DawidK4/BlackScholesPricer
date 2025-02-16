import streamlit as st

def login_ui():
    """Simulates a pop-up login window using session state."""

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["show_login_modal"] = True  # Show the modal on app start

    if st.session_state["show_login_modal"]:
        login_container = st.empty()  # Create an empty container to simulate a modal

        with login_container.container():  # This creates the "pop-up"
            st.markdown("## 🔑 Authentication Required")
            choice = st.radio("Choose an option:", ["Log In", "Create an Account", "Continue without Account"])

            if choice == "Log In":
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")

                if st.button("Login"):
                    if username == "user" and password == "password":  # Replace with real auth logic
                        st.session_state["logged_in"] = True
                        st.session_state["show_login_modal"] = False  # Close modal
                        login_container.empty()  # Remove the modal
                        st.success(f"✅ Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")

            elif choice == "Create an Account":
                new_username = st.text_input("Choose a Username")
                new_password = st.text_input("Choose a Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                if new_password != confirm_password:
                    st.error("❌ Passwords do not match!")

                if st.button("Create Account"):
                    st.session_state["logged_in"] = True
                    st.session_state["show_login_modal"] = False  # Close modal
                    login_container.empty()  # Remove the modal
                    st.success(f"✅ Account created for {new_username}!")
                    st.rerun()

            elif choice == "Continue without Account":
                st.info("🔓 You are continuing as a guest.")
                st.session_state["logged_in"] = False
                st.session_state["show_login_modal"] = False  # Close modal
                login_container.empty()  # Remove the modal
                st.rerun()

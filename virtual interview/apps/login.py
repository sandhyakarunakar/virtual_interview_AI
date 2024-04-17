import streamlit as st
from PIL import Image
from passlib.hash import pbkdf2_sha256
from apps.utils import verify_login, get

def login():
    #background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: rgba(137, 207, 240, 0.5); /* Adjust the RGBA values and opacity as needed */
        }
        .stTextInput>div>div>input {
            color: #2d3436 !important;
            background-color: #dfe6e9 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.form(key='login_form'):
        image = Image.open("images/login.png")
        st.image(image)

        
        st.markdown("<style>div[data-testid='stForm'] {border: 2px solid darkblue; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);}</style>", unsafe_allow_html=True)
        # st.subheader(":blue[Login]")
        st.markdown("<h3 style='color: darkblue;'>Login</h2>", unsafe_allow_html=True)
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        # Custom styling for the submit button
        submit_button_style = """
            <style>
                .stButton>button {
                    background-color: darkblue !important;
                    color: white !important;
                }
            </style>
        """
        st.markdown(submit_button_style, unsafe_allow_html=True)

        submit_button = st.form_submit_button(label='Login')

        if submit_button:
            if verify_login(username, password):
                state = get()
                state['is_logged_in'] = True
                state['username'] = username
                st.success('Logged in successfully!')
                st.balloons()

                st.rerun()  # Rerun the app to navigate to the dashboard
            else:
                st.error('Invalid username or password')


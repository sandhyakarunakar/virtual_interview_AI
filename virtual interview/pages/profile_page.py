# app/profile_page.py
import streamlit as st
from PIL import Image
import pandas as pd
from apps.utils import get,get_connection

state = get()

# Function to display the performance table for the logged-in user
def display_performance_table_by_user():
    st.subheader('Performance Table')
    state = get()
    user_id = state['user_id']
    with get_connection() as conn:
        # Fetch performance data for the logged-in user
        query = f'''
        SELECT attempts, marks
        FROM performance
        WHERE user_id = ?
        '''
        performance_data = pd.read_sql_query(query, conn, params=(user_id,))
    
    # Display the performance data
    st.write(performance_data)


# Check if the user is logged in
if not state['is_logged_in']:
    st.error('Please log in to view this page.')
else:
    # Logout button
    if st.button('Logout'):
        state['is_logged_in'] = False
        st.rerun()  # Rerun the app to go back to the login/register page
        
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
    # Create two columns layout
    col1, col2 = st.columns([2, 1])

    # Content for the first column
    with col1:
        # Add CSS style for the header text color
        st.markdown("<h1 style='color: darkblue;'>Profile Page</h1>", unsafe_allow_html=True)
        user_name = state["username"]
        # Display the subheader with the specified text color using markdown
        st.markdown(f'<h2 style="color: orange;">Welcome, {user_name}! 😊</h2>', unsafe_allow_html=True)
        # Add the content specific to the profile page here
        st.write('Keep up the enjoyment in learning and continue your journey forward!')

    # Content for the second column
    with col2:
        # Load and display the image from the images/profile.png file
        image = Image.open("images/profile.png")
        # st.image(image, caption=user_name + "'s Profile Image", use_column_width=True)
        st.image(image, caption=user_name + "'s Profile Image", use_column_width=True)
        st.write(f'<style>img {{border-radius: 15px;}}</style>', unsafe_allow_html=True)

    # Call the function with the user_id
    display_performance_table_by_user()
# app/profile_page.py
import streamlit as st
from PIL import Image
import pandas as pd
from apps.utils import get, get_connection

state = get()

# Function to display the performance table for the logged-in user
def display_performance_table_by_user():
    st.markdown("<h3 style='color: green;'>Performance Table</h3>", unsafe_allow_html=True)
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
    
    # Display only the last 5 rows and provide a scrollbar
    with st.expander("Click to view last 5 attempts of performance data", expanded=True):
        st.dataframe(performance_data.tail(5))

# Function to display links
def display_links():
    st.markdown("<h3 style='color: green;'>Learning Links:</h3>", unsafe_allow_html=True)
    
    with st.expander("Click to view Learning Links for Interview.", expanded=True):
        st.markdown("- [Link 1](https://github.com/FAQGURU/FAQGURU/tree/master/topics/en)")
        st.markdown("- [Link 2](https://github.com/twowaits/SDE-Interview-Questions)")
        st.markdown("- [Link 3](https://github.com/FAQGURU/FAQGURU/tree/master/topics/en)")

# Check if the user is logged in
if not state['is_logged_in']:
    st.error('Please log in to view this page.')
else:
    # Logout button
    if st.button('Logout'):
        state['is_logged_in'] = False
        st.rerun()  # Rerun the app to go back to the login/register page
        
    # Background color
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
    st.markdown("<h1 style='color: darkblue;'>Profile Page</h1>", unsafe_allow_html=True)
    # Create two rows layout
    row1 = st.columns(2)

    # Content for col1 and col2 in row1
    with row1[0]:
        # Content for col1
        user_name = state["username"]
        # Display the subheader with the specified text color using markdown
        st.markdown(f'<h2 style="color: orange;">Welcome, {user_name}! 😊</h2>', unsafe_allow_html=True)
        # Add the content specific to the profile page here
        st.write('Keep up the enjoyment in learning and continue your journey forward!')

    with row1[1]:
        # Content for col2
        # Load and display the image from the images/profile.png file
        image = Image.open("images/profile.png")
        st.image(image, caption=user_name + "'s Profile Image", width=200)
        st.write(f'<style>img {{border-radius: 15px;}}</style>', unsafe_allow_html=True)

    # Create the second row layout
    row2 = st.columns(2)

    # Content for col3 and col4 in row2
    with row2[0]:
        # Content for col3
        # Call the function to display the performance table
        display_performance_table_by_user()

    with row2[1]:
        # Content for col4
        # Call the function to display links
        display_links()

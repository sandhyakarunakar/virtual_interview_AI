# app/dashboard.py
import streamlit as st
from apps.utils import get, get_connection, create_performance_table
import os
import pandas as pd
from io import BytesIO
import plotly.express as px


def plot_performance():
    user_state = get()
    if user_state['is_logged_in']:
        username = user_state['username']
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.attempts, p.marks
                FROM performance p
                JOIN users u ON p.user_id = u.id
                WHERE u.username = ?
            ''', (username,))
            data = cursor.fetchall()
            if data:
                df = pd.DataFrame(data, columns=['attempts', 'marks'])
                # Plot line chart with Plotly
                fig = px.line(df, x='attempts', y='marks', title='Your Performance Line Chart')
                fig.update_layout(
                    xaxis_title='Attempts',
                    yaxis_title='Marks',
                    height=350,
                    width=350,
                    margin=dict(l=0, r=0, b=0, t=30),
                ) 
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No performance data is available for the logged-in user. Please take a virtual interview.")
    else:
        st.write("Please log in to view performance data.")

def show_dashboard():
    # Ensure that the necessary tables exist in the database
    create_performance_table()

    # st.title(f'Welcome, {get()["username"]}!')

    #background color
    st.markdown(
        """
        <style>
        .stApp{
        background-color: #D3D3D3;
        }
        .stTextInput>div>div>input {
            color: #2d3436 !important;
            background-color: #dfe6e9 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button('Logout'):
        state = get()
        state['is_logged_in'] = False
        st.rerun()  # Rerun the app to go back to the login/register page

    st.subheader("Performance Line Chart")
    
    # Display the performance line chart
    plot_performance()

    st.subheader("Click the button below to upload a PDF file.")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Create a folder to store uploaded files if it doesn't exist
        upload_folder = "upload_files"
        os.makedirs(upload_folder, exist_ok=True)

        # Save the uploaded file to the upload folder
        file_path = os.path.join(upload_folder, uploaded_file.name)
        with open(file_path, "wb") as file:
            file.write(uploaded_file.getvalue())
        st.balloons()
        st.success(f"File uploaded successfully! Saved at: {file_path}")

# app/practice_page.py
import streamlit as st
from apps.utils import get, get_connection
import spacy
import docx2txt
import fitz  # PyMuPDF
import os
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import speech_recognition as sr
import pandas as pd
import pyttsx3

UPLOAD_FOLDER = 'upload_files'

nlp = spacy.load('en_core_web_sm')

def get_files(UPLOAD_FOLDER):
    # Get the list of files in the uploaded folder
    files = os.listdir(UPLOAD_FOLDER)

    if not files:
        # No files uploaded, handle this condition (e.g., return an empty list or show a message)
        return []

    # Use the top file (assuming the first file in the list) for further processing
    top_file = files[0]
    file_path = os.path.join(UPLOAD_FOLDER, top_file)

    # Extract skills from the resume text
    skills = list(extract_skills_from_resume(file_path))
    return skills

def extract_skills_from_resume(pdf_path):
    # Load spaCy English model
    # Read PDF content using PyMuPDF
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    # Process text using spaCy
    doc = nlp(text)

    # Define a list of skills (you can customize this list based on your requirements)
    skills_list = ["java", "python", "html", "sql", "machine learning", "DSA", "Data Structures and Algorithms"]

    # Extract skills using spaCy and regular expressions
    extracted_skills = []
    for token in doc:
        # Check if the token is a skill (in this example, we're using a simple case-insensitive check)
        if any(re.search(skill, token.text, re.IGNORECASE) for skill in skills_list):
            cleaned_skill = token.text.replace('\uf020', '').strip()  # Remove special character
            extracted_skills.append(cleaned_skill.lower())

    # Remove duplicates
    unique_skills = list(set(extracted_skills))

    return unique_skills

def create_dict_from_csv(skills):
    dict1 = {}
    for skill in skills:
        csv_path = f'csv_files/{skill}.csv'
        if os.path.isfile(csv_path):
            data = pd.read_csv(csv_path)
            rows = data.sample(n=2, replace=False)
            skill_dict = {}
            for index, row in rows.iterrows():
                skill_dict[row.iloc[0]] = row.iloc[1]
            dict1[skill] = skill_dict
    return dict1

def speak_function(state):
    total_marks = 0
    dict1 = create_dict_from_csv(skills)

    # Create an empty container for the text
    result_container = st.empty()
    ans_skill = {}
    
    # Fetch the maximum attempts for the user
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(attempts) FROM performance WHERE user_id=?', (state['user_id'],))
        max_attempts = cursor.fetchone()[0] or 0  # If max_attempts is None, set it to 0
    
    # Increment the attempts counter for each skill
    attempts = max_attempts + 1
    
    # Insert data into the performance table
    with get_connection() as conn:
        cursor = conn.cursor()
        for i, j in dict1.items():
            marks = 0
            for key, value in j.items():
                engine = pyttsx3.init()

                # Update the text within the container
                result_container.markdown(
                    f"""
                    <div style='background-color: #c5c6c7; padding: 20px; border-radius: 10px; margin: 10px 0; width: 700px; height: 200px;'>
                        <p style='font-size: 20px; margin-bottom: 10px; color: #000000 ;'>Question:</p>
                        <p style='font-size: 16px;'>{key}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                engine.say(key)
                engine.runAndWait()
                r = sr.Recognizer()

                with sr.Microphone() as source:
                    print("Speak now...")
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    user_response = r.recognize_google(audio, language='en_in').lower()
                except sr.UnknownValueError:
                    user_response = ""
                except sr.RequestError:
                    user_response = ""
                print(user_response)

                accuracy = calculate_accuracy(key, user_response)
                print(accuracy)
                if accuracy > 0.5:
                    marks += 1
            
            ans_skill[i] = marks
            
    cursor.execute('''
        INSERT INTO performance (user_id, attempts, marks) VALUES (?, ?, ?)
    ''', (state['user_id'], attempts, marks))
    conn.commit()
    
    # Increment attempts for the next skill
    attempts += 1

    # Generate result table
    result_table = "<table style='border-collapse: collapse; width: 100%;'>"
    result_table += "<tr><th>Skill</th><th>Marks</th><th>Percentage</th><th>Remark</th></tr>"

    for i, j in ans_skill.items():
        remark = int((j / 2) * 100)

        if remark > 50:
            remark_text = "Excellent, Keep Going"
        elif 30 <= remark <= 50:
            remark_text = "Very good"
        else:
            remark_text = "Bad, try again"

        result_table += f"<tr><td>{i}</td><td>{j}</td><td>{remark}%</td><td>{remark_text}</td></tr>"

    result_table += "</table>"

    # Display the table using st.markdown
    st.markdown(result_table, unsafe_allow_html=True)

    # Calculate total marks
    total_marks = sum(ans_skill.values())
    
    # Display final result
    total_length = sum(len(inner_dict) for inner_dict in dict1.values())
    result_container.markdown(
        f"""
        <div style='background-color: #c5c6c7; padding: 20px; border-radius: 10px; margin: 10px 0; width: 700px; height: 200px;'>
            <p style='font-size: 30px; margin-bottom: 10px;'>Virtual interview is completed 🤩</p>
            <p style='font-size: 20px;'>Final Result: {total_marks}/{total_length}</p>
            <p style='font-size: 20px; margin-bottom: 10px;'>Improve Your skills and Communication. Good Luck 😊</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.balloons()

    return total_marks

def calculate_accuracy(sentence1, sentence2):
    # Use spaCy for tokenization, lemmatization, and stopword removal
    doc1 = nlp(sentence1)
    doc2 = nlp(sentence2)
    
    # Combine lemmatized tokens excluding stop words
    tokens1 = [token.lemma_ for token in doc1 if not token.is_stop]
    tokens2 = [token.lemma_ for token in doc2 if not token.is_stop]
    
    # Combine tokens into a string
    processed_sentence1 = ' '.join(tokens1)
    processed_sentence2 = ' '.join(tokens2)
    
    # Calculate cosine similarity using CountVectorizer
    vectorizer = CountVectorizer().fit_transform([processed_sentence1, processed_sentence2])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0, 0]

    return similarity



state = get()

# Check if the user is logged in
if not state['is_logged_in']:
    st.error('Please log in to view this page.')
else:
    st.header('Virtual Interview')
    # st.write('Before start the interview, Please upload your resume pdf in main page.')
    # st.write ('If already done feel free to take the interview.')

    skills = get_files(UPLOAD_FOLDER)
    # st.write(skills)
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
    # Create a button to start the virtual interview
    start_button_clicked = st.button('Start Virtual Interview')

    # Check if the button is clicked
    if start_button_clicked:
        # Hide the button by setting its visibility to False
        st.markdown(
            '''
            
            <style>div.row-widget.stButton > button{visibility:hidden}</style>''',
              unsafe_allow_html=True
        )
        
        # Call the speak_function with the state variable
        marks = speak_function(state)
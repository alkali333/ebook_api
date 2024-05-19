import streamlit as st
import requests
import pdfkit

# Define the URL of your FastAPI application
url = "http://localhost:8000/create_ebook"

# Create a form
with st.form(key="ebook_form"):
    title = st.text_input(label="Title")
    description = st.text_input(label="Description")
    number_of_chapters = st.number_input(label="Number of Chapters", min_value=1)
    words_per_chapters = st.number_input(label="Words per Chapter", min_value=1)
    model = st.text_input(label="Model", value="gpt-3.5-turbo")
    api_key = st.text_input(label="API Key")
    submit_button = st.form_submit_button(label="Create Ebook")

# When the form is submitted
if submit_button:
    # Define the payload
    payload = {
        "title": title,
        "description": description,
        "number_of_chapters": number_of_chapters,
        "words_per_chapter": words_per_chapters,
        "model": model,
        "api_key": api_key,
    }

    with st.spinner("Creating Ebook..."):
        response = requests.post(url, json=payload)

    if response.status_code == 200:
        ebook_content = response.json()["ebook_content"]

        file_name = f'{title.strip().replace(" ", "_")}.pdf'
        file_path = f"/home/alkai333/ebook-writer-api/ebooks/{file_name}"

        try:
            pdfkit.from_string(ebook_content, file_path, options={"encoding": "UTF-8"})
        except Exception as e:
            st.error(f"An error occurred while creating the PDF: {e}")
            raise

        st.success("Ebook content written to file successfully!")

        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")
            raise

        st.download_button("Download Ebook", data, file_name, "application/pdf")

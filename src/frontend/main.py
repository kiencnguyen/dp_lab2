import requests
import streamlit as st
from PIL import Image


def fetch_data(question):
    """
    Post the question for FastAPI endpoint and get the answer
    :param question
    :return: response in json format
    """
    response = requests.post("http://backend:8000/query", json={"input_text": question})
    return response.json()


def display_prompt():
    """
    Display the prompt "Type your question here and press Enter"
    with font_size and font_color
    """

    css_string = """
                <style>
                .custom-header {
                    font-size: 30px;
                    font-weight: bold;
                    color: #2035E8;  
                }
                </style>
                <h2 class="custom-header">Type your question here and press submit button</h2>
                """

    st.markdown(
        css_string,
        unsafe_allow_html=True
    )


def display_answer_header():
    """
    Display the string "Answer" with font_size and font_color
    """

    css_string = """
                <style>
                .custom-header {
                    font-size: 30px;
                    font-weight: bold;
                    color: #2035E8;  
                }
                </style>
                <h2 class="custom-header">Answer</h2>
                """

    st.markdown(
        css_string,
        unsafe_allow_html=True
    )


def main():

    st.set_page_config(page_title="Financial Information")
    image = Image.open('./src/frontend/Logo_IUH.png')
    st.image(image, use_column_width=True)

    st.header("Financial Information")
    st.subheader("Kien C Nguyen")

    display_prompt()

    # Initialize session state for the text area if it doesn't exist
    if 'text' not in st.session_state:
        st.session_state['text'] = ""
    # Show text area
    st.text_area("Enter your text here:", height=100, key='text', label_visibility="hidden")


    # Function to clear the text area
    def clear_text():
        st.session_state['text'] = ""

    with st.form("myform"):
        submit_button, clear_button = st.columns([1, 1])
        with submit_button:
            submit = st.form_submit_button(label="Submit")
        with clear_button:
            st.form_submit_button(label="Clear", on_click=clear_text)

    if submit and st.session_state['text']:

        # Call fetch_data() to post the question to FastAPI endpoint
        returned_data = fetch_data(st.session_state['text'])
        response = returned_data.get("answer", "")

        # Display the response from FastAPI endpoint
        display_answer_header()
        st.write(response)


#######################################################################
if __name__ == "__main__":
    main()


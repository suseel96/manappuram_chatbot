from utils.chatbot import chat_interactions
import streamlit as st
import os
from utils.translation import translationUtils


def main():
    max_retries = 2
    image_path = os.path.join(os.getcwd(), "utils", "MFL-logo.png")
    st.image(
        image_path,
        width=150,
    )
    st.title("Chatbot for Manappuram Finance Limited")

    # Custom CSS to change the button color and placeholder text color
    st.markdown(
        """
        <style>
        .stButton > button {
            color: white;
            background-color: #0066cc;
            border-color: #0066cc;
        }
        .stButton > button:hover {
            background-color: #005cb8;
            border-color: #005cb8;
        }
        .stTextInput > div > div > input::placeholder {
            color: white;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Form to handle user input and submit
    with st.form(key="chat_form"):
        col1, col2 = st.columns([1, 3])

        with col1:
            options = list(translationUtils().language_map.values())
            selected_language = st.selectbox(
                "Select language",
                options,
                index=list(translationUtils().language_map.values()).index("English"),
            )
        with col2:
            user_input = st.text_input(
                "User input:", placeholder="Type your query here..."
            )

        submit_button = st.form_submit_button(label="Send")

    # When the form is submitted, get the chatbot response
    if submit_button and user_input:
        try_count = 1
        response = en_llm_response = "Sorry could not answer"
        while (try_count <= max_retries) and (
            en_llm_response == "Sorry could not answer"
        ):
            response, en_llm_response = chat_interactions(selected_language, user_input)
            print(en_llm_response, try_count)
            try_count += 1
        st.markdown(response)


if __name__ == "__main__":
    main()

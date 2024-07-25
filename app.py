from utils.chatbot import chat_interactions
import streamlit as st
import os


def main():
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
        user_input = st.text_input("User input:", placeholder="Type your query here...")
        submit_button = st.form_submit_button(label="Send")

    # When the form is submitted, get the chatbot response
    if submit_button and user_input:
        response = chat_interactions(user_input)
        st.markdown(response)


if __name__ == "__main__":
    main()

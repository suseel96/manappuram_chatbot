import os
import json
import warnings
import pandas as pd
import streamlit as st
from openai import OpenAI
import anthropic
from dotenv import load_dotenv

from utils.weaviate import weaviateUtils
from utils.translation import translationUtils
warnings.filterwarnings("ignore")

load_dotenv()

def questionAnsweringUsingClaude(context, en_lang_input):
    try:
        qa_prompt = f'''Given the following context, please answer the question using the context:
                    Context: {context}
                    Question: {en_lang_input}
                    Provide a concise answer based solely on the information given in the context. 
                    If the information is not present in the context, state that you don't have enough information to answer. 
                    Do not make assumptions or provide information beyond what is explicitly stated in the context and do not respond with anything (conclusive statements like 'according to context' etc) apart from the answer.
                    If you are not able to answer respons saying ''Sorry could not answer''
                    ''' 
        anthropic_client = anthropic.Anthropic()
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens = 1024,
            messages=[
                {"role": "user", "content": qa_prompt}
            ]
        )

        anthropic_response = message.content[0].text.strip()
        return anthropic_response
    except Exception as e:
        return False


def questionAnsweringUsingOpenai(context, en_lang_input):
    try:
        qa_prompt = f"""Given the following context, please answer the question using the context:
                    Context: {context}
                    Question: {en_lang_input}
                    Provide a detailed answer based solely on the information given in the context.
                    Make sure the response does not exceed 1000 characters.
                    If the information is not present in the context, state that you don't have enough information to answer. 
                    Do not make assumptions or provide information beyond what is explicitly stated in the context and do not respond with anything (conclusive statements like 'according to context' etc) apart from the answer.
                    If you are not able to answer respons saying ''Sorry could not answer''                    """
        openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        message = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=1024,
            messages=[{"role": "user", "content": qa_prompt}],
        )
        openai_response = message.choices[0].message.content.strip()
        return openai_response
    except Exception as e:
        return False


def chat_interactions(selected_language, native_lang_input):
    try:
        host = st.secrets["WEAVIATE_HOST"]
        port = st.secrets["WEAVIATE_PORT"]
        cohere_api_key = st.secrets["COHERE_API_KEY"]
        additional_headers = {"X-Cohere-Api-Key": cohere_api_key}
        weaviate_obj = weaviateUtils(host, port, additional_headers)
        default_error_msg = "Sorry, could not answer your query. Please try again."
        translation_obj = translationUtils()
        selected_language_code = [
            i for i, j in translation_obj.language_map.items() if j == selected_language
        ][0]

        if selected_language_code != 'en':
            transliteration_resp = translation_obj.transliterateInput(
                selected_language, native_lang_input
            )
            if not transliteration_resp:
                return default_error_msg
            en_lang_input = transliteration_resp
        else:
            en_lang_input = native_lang_input
        vector_search_response = weaviate_obj.performVectorSearch(en_lang_input)
        df = pd.DataFrame(vector_search_response["data"]["Get"]["Manapuram_v1"])
        df = pd.concat([df, pd.json_normalize(df['_additional'])], axis=1).drop('_additional', axis=1)
        df.sort_values('score', ascending=False, inplace=True)
        context = df.head(2)[['title','section','subsection','content']].to_json(orient='records')
        # llm_response = questionAnsweringUsingClaude(context, en_lang_input)
        en_llm_response = questionAnsweringUsingOpenai(context, en_lang_input)
        if not en_llm_response:
            return default_error_msg

        if selected_language_code != 'en':
            final_resp = translation_obj.translateText(
                source_language="en",
                target_language=selected_language_code,
                native_lang_input=en_llm_response,
            )
            if not final_resp:
                final_resp = default_error_msg
        else:
            final_resp = en_llm_response
        return final_resp, en_llm_response
    except Exception as e:
        return default_error_msg, en_llm_response

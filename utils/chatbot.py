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
                    Provide a concise answer based solely on the information given in the context. 
                    If the information is not present in the context, state that you don't have enough information to answer. 
                    Do not make assumptions or provide information beyond what is explicitly stated in the context and do not respond with anything (conclusive statements like 'according to context' etc) apart from the answer.
                    If you are not able to answer respons saying ''Sorry could not answer''
                    """
        openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        message = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=1024,
            messages=[{"role": "user", "content": qa_prompt}],
        )
        openai_response = message.choices[0].message.content.strip()
        return openai_response
    except Exception as e:
        return str(e)

def chat_interactions(native_lang_input):
    try:
        # host = os.environ['WEAVIATE_HOST']
        # port = os.environ['WEAVIATE_PORT']
        # cohere_api_key = os.environ['COHERE_API_KEY']
        # additional_headers = {"X-Cohere-Api-Key": cohere_api_key}
        host = st.secrets["WEAVIATE_HOST"]
        port = st.secrets["WEAVIATE_PORT"]
        cohere_api_key = st.secrets["COHERE_API_KEY"]
        additional_headers = {"X-Cohere-Api-Key": cohere_api_key}
        weaviate_obj = weaviateUtils(host, port, additional_headers)
        default_error_msg = "Sorry, could not answer your query. Please try again."
        translation_obj = translationUtils()
        src_lang = translation_obj.detectLang(native_lang_input)
        if src_lang is None:
            return default_error_msg
        elif src_lang != 'en':
            en_lang_input = translation_obj.translateText(
                source_language=src_lang,
                target_language="en",
                native_lang_input=native_lang_input,
            )
            if not en_lang_input:
                return default_error_msg
        else:
            en_lang_input = native_lang_input
        vector_search_response = weaviate_obj.performVectorSearch(en_lang_input)
        df = pd.DataFrame(vector_search_response['data']['Get']['Manapuram'])
        df = pd.concat([df, pd.json_normalize(df['_additional'])], axis=1).drop('_additional', axis=1)
        df.sort_values('score', ascending=False, inplace=True)
        context = df.head(2)[['title','section','subsection','content']].to_json(orient='records')
        # llm_response = questionAnsweringUsingClaude(context, en_lang_input)
        llm_response = questionAnsweringUsingOpenai(context, en_lang_input)
        if not default_error_msg:
            return default_error_msg

        if src_lang != 'en':
            final_resp = translation_obj.translateText(
                source_language="en",
                target_language=src_lang,
                native_lang_input=llm_response,
            )
        else:
            final_resp = llm_response

        return final_resp
    except Exception as e:
        return default_error_msg

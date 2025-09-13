import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

def get_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response['choices'][0]['message']['content']

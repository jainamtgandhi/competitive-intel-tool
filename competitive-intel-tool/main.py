import streamlit as st
from scraper import fetch_website_content
from gpt import get_gpt_response
from prompt_template import build_ci_prompt

st.set_page_config(page_title="CI Tool", layout="wide")
st.title("🧠 Competitive Intelligence Tool")

company = st.text_input("Company Name", placeholder="e.g., SonarSource")
url = st.text_input("Company Website", placeholder="https://example.com")

if st.button("Run Analysis") and company and url:
    with st.spinner("Fetching content and generating insights..."):
        content = fetch_website_content(url)
        prompt = build_ci_prompt(company, content)
        result = get_gpt_response(prompt)

    st.markdown("### 🔍 Competitive Intelligence Summary")
    st.markdown(result)
    st.download_button("📥 Download Report", result, file_name=f"{company}_CI.txt")

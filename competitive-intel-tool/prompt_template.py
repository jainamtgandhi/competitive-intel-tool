def build_ci_prompt(company_name, content):
    return f"""
Act as a Competitive Intelligence expert. Based on the following content from {company_name}, answer these:

1. What does this company do?
2. Who are their target personas?
3. What value propositions do they highlight?
4. What is their messaging tone?
5. What product features are emphasized?
6. What is their pricing model (if visible)?
7. What go-to-market channels do they use?
8. Who are 2–3 competitors?

CONTENT:
{content}

Answer each question in clear bullet points.
"""

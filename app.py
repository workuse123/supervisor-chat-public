import os
import requests
import streamlit as st
from databricks.sdk import WorkspaceClient

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_CLIENT_ID = os.getenv("DATABRICKS_CLIENT_ID")
DATABRICKS_CLIENT_SECRET = os.getenv("DATABRICKS_CLIENT_SECRET")
ENDPOINT = os.getenv("SERVING_ENDPOINT", "mas-58a5288f-endpoint")

w = WorkspaceClient(
    host=DATABRICKS_HOST,
    client_id=DATABRICKS_CLIENT_ID,
    client_secret=DATABRICKS_CLIENT_SECRET,
)

host = w.config.host.rstrip("/")
if not host.startswith("http"):
    host = "https://" + host
URL = f"{host}/serving-endpoints/{ENDPOINT}/invocations"

def ask_agent(messages):
    headers = w.config.authenticate()
    headers["Content-Type"] = "application/json"
    r = requests.post(URL, headers=headers, json={"input": messages}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text}")
    data = r.json()
    texts = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    texts.append(c.get("text", ""))
    if texts:
        return texts[-1]
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return str(data)

st.title("Ask the Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_agent(st.session_state.messages)
            except Exception as e:
                answer = f"Sorry, something went wrong: {e}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

%python
import gradio as gr
from databricks.sdk import WorkspaceClient
import os

# Set your Databricks credentials here or use environment variables
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "https://<your-workspace>.cloud.databricks.com")
DATABRICKS_CLIENT_ID = os.getenv("DATABRICKS_CLIENT_ID", "<your-client-id>")
DATABRICKS_CLIENT_SECRET = os.getenv("DATABRICKS_CLIENT_SECRET", "<your-client-secret>")
ENDPOINT_NAME = os.getenv("SERVING_ENDPOINT", "mas-58a5288f-endpoint")

w = WorkspaceClient(
    host=DATABRICKS_HOST,
    client_id=DATABRICKS_CLIENT_ID,
    client_secret=DATABRICKS_CLIENT_SECRET,
)

# Example function to call Databricks model serving endpoint
def chat_fn(message, history):
    host = w.config.host.rstrip("/")
    if not host.startswith("http"):
        host = "https://" + host
    url = f"{host}/serving-endpoints/{ENDPOINT_NAME}/invocations"
    headers = w.config.authenticate()
    headers["Content-Type"] = "application/json"
    # Send chat history if endpoint supports it, else just last message
    try:
        response = requests.post(url, headers=headers, json={"input": [message]}, timeout=300)
        if response.status_code == 200:
            data = response.json()
            answer = str(data.get("output", "No response"))
        else:
            answer = f"Error: {response.status_code} {response.text}"
    except Exception as e:
        answer = f"Exception: {e}"
    return answer

gr.ChatInterface(chat_fn).launch(share=True)

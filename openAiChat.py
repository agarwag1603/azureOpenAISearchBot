import os
from flask import Flask, render_template, request
from openai import AzureOpenAI

# Initialize Flask app
app = Flask(__name__)

# Load environment variables (or you can replace them with hardcoded values)
endpoint = os.getenv("ENDPOINT_URL", "https://gaura-m5azl4rc-eastus.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "companychatbot")
search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://aisearchservice1603.search.windows.net")
search_key = os.getenv("SEARCH_KEY", "")
search_index = os.getenv("SEARCH_INDEX_NAME", "searchpdfindex")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview"
)

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    response = ""
    if request.method == "POST":
        user_input = request.form["user_input"]

        # Prepare the chat prompt
        chat_prompt = [
            {
                "role": "system",
                "content": "You are an AI assistant that helps people find information only about the pdf upload from the dataset."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        # Call Azure OpenAI API to get a response
        try:
            completion = client.chat.completions.create(
                model=deployment,
                messages=chat_prompt,
                extra_body={
                    "data_sources": [{
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": search_endpoint,
                            "index_name": search_index,
                            "semantic_configuration": "default",
                            "query_type": "semantic",
                            "fields_mapping": {},
                            "in_scope": True,
                            "role_information": "You are an AI assistant that helps people find information only about the pdf upload from the dataset",
                            "filter": None,
                            "strictness": 3,
                            "top_n_documents": 5,
                            "authentication": {
                                "type": "api_key",
                                "key": search_key
                            }
                        }
                    }]
                }
            )
            # Get the response message from the Azure OpenAI completion
            response = completion.choices[0].message.content
        except Exception as e:
            response = f"Error: {e}"

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Change the port number here

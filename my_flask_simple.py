#!/usr/bin/env python
# coding: utf-8

# In[30]:


from llama_index.llms.azure_openai import AzureOpenAI

import logging
import sys
import json


logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
import base64
import requests

client_id = 'cG9jLXRyaWFsMjAyM09jdG9iZXIxNwff_540f3843f35f87eeb7b238fc2f8807'
client_secret = 'b-mQoS2NXZe4I15lVXtY7iBHCAg9u7ufZFx7MZiOHAFlzRBkFmOaenUI2buRpRBb'

# print(base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8'))
token_url = "https://id.cisco.com/oauth2/default/v1/token"
llm_endpoint="https://chat-ai.cisco.com"
auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth_key}",
}

# Make a POST request to retrieve the token
token_response = requests.post(token_url, headers=headers, data="grant_type=client_credentials")
token = token_response.json().get("access_token")

user_param = json.dumps({"appkey": "egai-prd-wws-log-chat-data-analysis-1"})
appkey="egai-prd-wws-log-chat-data-analysis-1"

llm = AzureOpenAI(azure_endpoint=llm_endpoint,
                  #model= 'gpt-4o-mini',
                  api_version="2024-07-01-preview",
                  deployment_name='gpt-4o-mini',
                  api_key=token,
                  max_tokens=16000,
                  temperature=0,
                  additional_kwargs={"user": f'{{"appkey": "{appkey}"}}'}
                 )


# In[31]:


### use it only if you need openAI, not for local LLM
import nest_asyncio 
nest_asyncio.apply()

# For OpenAI

import os
import logging
import sys

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output


# define LLM

from llama_index.core import Settings

Settings.llm = llm
#Settings.chunk_size = 512
# maximum input size to the LLM
Settings.context_window = 3000

# number of tokens reserved for text generation.
Settings.num_output = 256


# In[32]:


# use Huggingface embeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

#embed_model = HuggingFaceEmbedding(model_name="jinaai/jina-embeddings-v2-base-en")
Settings.embed_model=embed_model


# In[4]:


import os
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
)



# In[6]:


documents = SimpleDirectoryReader("/app/show_cmd/").load_data()


# In[7]:


Settings.chunk_size = 1024
nodes = Settings.node_parser.get_nodes_from_documents(documents)


# In[33]:


from llama_index.core import StorageContext

# initialize storage context (by default it's in-memory)
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)


# In[34]:


from llama_index.core import SummaryIndex
from llama_index.core import VectorStoreIndex

summary_index = SummaryIndex(nodes, storage_context=storage_context)
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)


# In[35]:


list_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)
vector_query_engine = vector_index.as_query_engine()


# In[36]:


from llama_index.core.tools import QueryEngineTool


list_tool = QueryEngineTool.from_defaults(
    query_engine=list_query_engine,
    description=(
        "Useful for summarization questions related to cisco router"
        " show command output"
    ),
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=(
        "Useful for retrieving specific context related cisco router"
        "show command output"
    ),
)


# In[37]:


from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)


query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[
        list_tool,
        vector_tool,
    ],
)


# In[40]:


response = query_engine.query("from the cisco output of the router, check if i have 2  ospf neighbors")
print(str(response))


# In[ ]:


#better formated flask


from flask import Flask, request, render_template_string
from markupsafe import Markup
from llama_index.core import (
    load_index_from_storage,
    load_indices_from_storage,
    load_graph_from_storage,
)

app = Flask(__name__)

# HTML template for the input form
form_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Query Interface</title>
</head>
<body>
  <h1>Enter your query</h1>
  <form action="/query" method="get">
    <input type="text" name="text" placeholder="Talk To The Data" required>
    <input type="submit" value="Go!">
  </form>
  {% if response %}
    <h2>Response:</h2>
    {{ response }}
  {% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    # Render the form template without a response
    return render_template_string(form_template)

@app.route("/query", methods=["GET"])
def query_index():
    query_text = request.args.get("text", None)
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    
    # Here you would have your logic to handle the query
    # For demonstration purposes, we'll just echo the query text
    response = query_engine.query(query_text)
    
    # Convert the response to a Markup object to preserve formatting
    formatted_response = Markup("<pre>{}</pre>".format(response))

    # Render the form template with the formatted response
    return render_template_string(form_template, response=formatted_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5601)


# In[ ]:





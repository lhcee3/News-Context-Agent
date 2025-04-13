import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import logging
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama, HuggingFaceHub
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent, Tool
from supabase import create_client, Client
from tools import get_latest_news
from flask_cors import CORS
import traceback



app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

vectorstore = SupabaseVectorStore(
    client=supabase,
    embedding=embedding_model,
    table_name="documents",
    query_name="match_documents"
)

def save_to_longterm_memory(user_query, bot_response):
    text = user_query + "\n" + (bot_response["output"] if isinstance(bot_response, dict) else bot_response)
    metadata = {
        "timestamp": str(datetime.now()),
        "source": "user_chat"
    }
    vectorstore.add_texts([text], metadatas=[metadata])

def retrieve_from_longterm_memory(query, k=3):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)

def get_llm():
    return (
        Ollama(model="mistral", base_url="http://localhost:11434")
        if USE_OLLAMA else
        HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.5, "max_length": 256})
    )

llm = get_llm()

short_term_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True
)

tools = [
    Tool(
        name="get_latest_news",
        func=get_latest_news,
        description="Get latest news for a topic"
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="chat-conversational-react-description",
    memory=short_term_memory,
    verbose=True
)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/", methods=["GET"])
def home():
    return "Backend is running ✅"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('query')
        app.logger.info("Received query: %s", query)

        if not query:
            return jsonify({"error": "No query provided"}), 400

        retrieved_docs = retrieve_from_longterm_memory(query)
        app.logger.debug("Retrieved from long-term memory: %s", retrieved_docs)

        response = agent.invoke(query)

        if not response:
            return jsonify({"error": "Empty response from agent"}), 500

        app.logger.debug("Full Response: %s", response)
        save_to_longterm_memory(query, response)

        return jsonify({"response": response})

    except Exception as e:
        app.logger.error("Error processing request: %s", str(e))
        return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

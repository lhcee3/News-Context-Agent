from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama, HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain, LLMChain
from langchain_core.runnables import RunnableLambda, RunnableBranch
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langgraph.graph import StateGraph, END
import os

# Toggle source: "ollama" or "huggingface"
USE = "ollama"

# Setup memory
memory = ConversationBufferMemory(return_messages=True)

# Output parser
parser = StrOutputParser()

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}")
])

# Load local Ollama model
ollama_llm = Ollama(model="mistral", temperature=0.7, callbacks=[StreamingStdOutCallbackHandler()])

# Load Hugging Face model
huggingface_llm = HuggingFaceHub(
    repo_id="google/flan-t5-large",
    model_kwargs={"temperature": 0.7, "max_new_tokens": 200}
)

# Select active LLM
def get_primary_llm():
    if USE == "ollama":
        return ollama_llm
    elif USE == "huggingface":
        return huggingface_llm
    else:
        raise ValueError("Unsupported LLM")

# Fallback logic
primary_llm_chain = LLMChain(llm=get_primary_llm(), prompt=prompt)
fallback_llm_chain = LLMChain(llm=huggingface_llm, prompt=prompt)

def try_primary_with_fallback(input_dict):
    try:
        return primary_llm_chain.invoke(input_dict)
    except Exception as e:
        print("[!] Primary LLM failed. Switching to fallback.")
        return fallback_llm_chain.invoke(input_dict)

# LangGraph setup
class ChatState(dict):
    pass

def respond(state):
    user_input = state["input"]
    result = try_primary_with_fallback({"input": user_input})
    return {"input": user_input, "response": result["text"]}

# LangGraph graph
builder = StateGraph(ChatState)
builder.add_node("llm_response", respond)
builder.set_entry_point("llm_response")
builder.add_edge("llm_response", END)
chat_graph = builder.compile()

# 🧪 Test run
if __name__ == "__main__":
    user_input = input("You: ")
    result = chat_graph.invoke({"input": user_input})
    print("\nAssistant:", result["response"])

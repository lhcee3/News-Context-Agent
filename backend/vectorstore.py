from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
from llm_setup import embeddings
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")

supabase_client = create_client(supabase_url, supabase_key)

vectorstore = SupabaseVectorStore(
    client=supabase_client,
    embedding=embeddings,
    table_name="documents"
)

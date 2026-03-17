import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.core.node_parser import SentenceSplitter


# טעינת משתני סביבה מה-.env שנמצא בשורש הפרויקט
load_dotenv()

def init_settings():
    """מאתחל את הגדרות המודלים הגלובליות של LlamaIndex"""
    
    # הגדרת ה-LLM (Groq)
    Settings.llm = Groq(
        model="llama-3.1-8b-instant", 
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    # הגדרת מודל ה-Embedding (Cohere)
    Settings.embed_model = CohereEmbedding(
        api_key=os.getenv("COHERE_API_KEY"),
        model_name="embed-multilingual-v3.0"
    )
    
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    print("⚙️ Settings initialized with Custom SentenceSplitter.")

    # הגדרות נוספות (כמו Chunk Size גלובלי אם תרצי)
    Settings.chunk_size = 512
    Settings.chunk_overlap = 20

    print("⚙️ Settings initialized successfully.")
import logging
import os
import openai
import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient
from config.config import OpenAiConsts


'''
TODO: add funtionality for overwiriting/updating embeddings in mongodb
TODO: add what is being embedded to logging
'''

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not MONGO_URI:
    logging.error("MONGO_URI is not set! Check your .env file.")
    raise ValueError("MONGO_URI is not set!")

if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is not set! Check your .env file.")
    raise ValueError("OPENAI_API_KEY is not set!")

# Connect to MongoDB
logging.info("Connecting to MongoDB Atlas...")
client = MongoClient(MONGO_URI, tls=True, serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")  # Test connection
    logging.info("Connected to MongoDB Atlas!")
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    raise e

db = client["privex-dev"]  # Database name
collection = db["agent_settings"]  # Collection name

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY

def generate_embedding(text):
    """Generate OpenAI embeddings for a given text"""
    if not text or text.strip() == "":  # Avoid sending empty text
        logging.warning("Skipping empty text for embedding.")
        return None

    logging.info(f"Generating embedding for text (length: {len(text)} chars)...")
    try:
        response = openai.embeddings.create(
            # model="text-embedding-ada-002",
            model= OpenAiConsts().DEFAULT_EMBEDDING_MODEL,
            input=text
        )
        logging.info("Embedding generated successfully.")
        return response.data[0].embedding

    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}")
        return None

def process_documents():
    """Fetch documents, generate embeddings, and update MongoDB"""
    logging.info("Fetching documents from MongoDB...")
    documents = collection.find({}, {"_id": 1, "persona": 1, "knowledgeBase": 1})

    count = 0
    for doc in documents:
        doc_id = doc["_id"]
        persona_text = doc.get("persona", "")
        knowledge_base_text = doc.get("knowledgeBase", "")

        logging.info(f"Processing document ID: {doc_id}")

        # Generate embeddings
        persona_embedding = generate_embedding(persona_text)
        knowledge_base_embedding = generate_embedding(knowledge_base_text)

        # Prepare update query
        update_query = {}
        if persona_embedding:
            update_query["persona_embeddings"] = persona_embedding
        if knowledge_base_embedding:
            update_query["knowledgeBase_embeddings"] = knowledge_base_embedding

        # Update MongoDB document with new embeddings
        if update_query:  # Only update if there's something new to insert
            collection.update_one({"_id": doc_id}, {"$set": update_query})
            logging.info(f"Updated document {doc_id} with embeddings.")
            count += 1

    logging.info(f"All documents processed successfully! {count} documents updated.")

# Run the script
# if __name__ == "__main__":
#     logging.info("Starting embedding process...")
#     process_documents()
#     logging.info("Embedding process completed!")
import os
import weaviate
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import OPENAI_API_KEY, WEAVIATE_URL, WEAVIATE_API_KEY, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from app.models.db_models import Document

class EmbeddingsService:
    """Service to handle text embeddings and vector search"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = EMBEDDING_MODEL
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        
        # Initialize Weaviate client
        if WEAVIATE_API_KEY and WEAVIATE_API_KEY.strip():
            # Initialize with API key
            self.weaviate_client = weaviate.Client(
                url=WEAVIATE_URL,
                auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
            )
        else:
            # Initialize without API key for local development or when API key auth is disabled
            self.weaviate_client = weaviate.Client(url=WEAVIATE_URL)
        
        # Initialize the schema if it doesn't exist
        self._initialize_schema()

    def _initialize_schema(self):
        """Initialize the Weaviate schema for our documents"""
        try:
            # Check if schema already exists
            schema = self.weaviate_client.schema.get()
            class_names = [c['class'] for c in schema['classes']] if 'classes' in schema else []
            
            # Create schema if it doesn't exist
            if 'TextChunk' not in class_names:
                class_obj = {
                    "class": "TextChunk",
                    "description": "A chunk of text from a management document",
                    "vectorizer": "none",  # We provide our own vectors
                    "properties": [
                        {
                            "name": "text",
                            "dataType": ["text"],
                            "description": "The text content of the chunk"
                        },
                        {
                            "name": "document_id",
                            "dataType": ["string"],
                            "description": "Reference to the source document ID"
                        },
                        {
                            "name": "chunk_index",
                            "dataType": ["int"],
                            "description": "Index of this chunk within the document"
                        },
                        {
                            "name": "document_title",
                            "dataType": ["string"],
                            "description": "Title of the source document"
                        },
                        {
                            "name": "metadata",
                            "dataType": ["text"],
                            "description": "Additional metadata as JSON string"
                        }
                    ]
                }
                
                self.weaviate_client.schema.create_class(class_obj)
                print("Created 'TextChunk' schema")
        
        except Exception as e:
            print(f"Error initializing Weaviate schema: {str(e)}")
    
    def get_embedding(self, text):
        """
        Get embedding for a text using OpenAI API
        
        Args:
            text (str): Text to get embedding for
            
        Returns:
            list: Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None
    
    def process_document(self, document_id=None):
        """
        Process a document and store its chunks in the vector database
        
        Args:
            document_id (str, optional): Document ID to process. If None, processes all documents.
            
        Returns:
            bool: Success status
        """
        try:
            documents = [Document.get_by_id(document_id)] if document_id else Document.get_all()
            
            for doc in documents:
                if not doc:
                    continue
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(doc["content"])
                
                # Process each chunk
                for i, chunk in enumerate(chunks):
                    # Get embedding for chunk
                    embedding = self.get_embedding(chunk)
                    if not embedding:
                        continue
                    
                    # Add to Weaviate
                    self.weaviate_client.data_object.create(
                        class_name="TextChunk",
                        data_object={
                            "text": chunk,
                            "document_id": str(doc["_id"]),
                            "chunk_index": i,
                            "document_title": doc["title"],
                            "metadata": str(doc["metadata"])
                        },
                        vector=embedding
                    )
            
            return True
        
        except Exception as e:
            print(f"Error processing document for vectorization: {str(e)}")
            return False
    
    def search(self, query, limit=5):
        """
        Search for relevant text chunks using semantic search
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of relevant text chunks with metadata
        """
        try:
            # Get embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []
            
            # Search in Weaviate
            result = (
                self.weaviate_client.query
                .get("TextChunk", ["text", "document_id", "document_title", "chunk_index", "metadata"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(limit)
                .do()
            )
            
            # Extract and format results
            chunks = []
            if "data" in result and "Get" in result["data"] and "TextChunk" in result["data"]["Get"]:
                chunks = result["data"]["Get"]["TextChunk"]
            
            return chunks
        
        except Exception as e:
            print(f"Error searching for text chunks: {str(e)}")
            return [] 
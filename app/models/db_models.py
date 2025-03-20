from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from app.config import MONGODB_URI, MONGODB_DB_NAME
import os
import json
import traceback

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.server_info()
    db = client[MONGODB_DB_NAME]
    # Collections
    queries_collection = db.queries
    graphs_collection = db.graphs
    documents_collection = db.documents
    connections_collection = db.connections
    contexts_collection = db.contexts
    MONGODB_CONNECTED = True
except Exception as e:
    print(f"Warning: Could not connect to MongoDB at {MONGODB_URI}: {str(e)}")
    print("Will use local file storage for documents instead.")
    MONGODB_CONNECTED = False

# Define local storage directory
LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'local_storage')
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

class Query:
    """Model for user queries"""
    
    @staticmethod
    def create(user_id, query_text, context_params=None):
        """Create a new query record"""
        query_doc = {
            "user_id": user_id,
            "query_text": query_text,
            "timestamp": datetime.utcnow(),
            "status": "processing",
            "context_params": context_params or {}
        }
        
        result = queries_collection.insert_one(query_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def update_status(query_id, status, graph_id=None):
        """Update the status of a query"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if graph_id:
            update_data["graph_id"] = graph_id
            
        queries_collection.update_one(
            {"_id": ObjectId(query_id)},
            {"$set": update_data}
        )
    
    @staticmethod
    def get_by_id(query_id):
        """Get a query by ID"""
        query = queries_collection.find_one({"_id": ObjectId(query_id)})
        return query
    
    @staticmethod
    def get_user_queries(user_id, limit=10):
        """Get recent queries for a user"""
        cursor = queries_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)


class Graph:
    """Model for decision graphs"""
    
    @staticmethod
    def create(query_id, graph_data):
        """Create a new graph record"""
        graph_doc = {
            "query_id": query_id,
            "graph_data": graph_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = graphs_collection.insert_one(graph_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(graph_id):
        """Get a graph by ID"""
        graph = graphs_collection.find_one({"_id": ObjectId(graph_id)})
        return graph
    
    @staticmethod
    def get_by_query_id(query_id):
        """Get a graph by query ID"""
        graph = graphs_collection.find_one({"query_id": query_id})
        return graph
    
    @staticmethod
    def update(graph_id, graph_data):
        """Update graph data"""
        graphs_collection.update_one(
            {"_id": ObjectId(graph_id)},
            {
                "$set": {
                    "graph_data": graph_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    @staticmethod
    def add_connections(graph_id, connections):
        """Add connection data to a graph"""
        for connection in connections:
            connection["graph_id"] = graph_id
            connection["created_at"] = datetime.utcnow()
            connections_collection.insert_one(connection)
    
    @staticmethod
    def get_connections(graph_id):
        """Get all connections for a graph"""
        connections = connections_collection.find({"graph_id": graph_id})
        return list(connections)
    
    @staticmethod
    def get_node_connections(graph_id, node_id):
        """Get connections for a specific node in a graph"""
        connections = connections_collection.find({
            "graph_id": graph_id,
            "$or": [
                {"source_id": node_id},
                {"target_id": node_id}
            ]
        })
        return list(connections)
    
    @staticmethod
    def filter_by_context(graph_id, context_params):
        """Filter graph nodes based on context parameters"""
        # This implementation would use the context params to 
        # determine relevance scores and filter/highlight nodes
        pass


class Document:
    """Model for textbook documents"""
    
    @staticmethod
    def create(title, content, metadata=None):
        """Create a new document record"""
        document_doc = {
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            if MONGODB_CONNECTED:
                result = documents_collection.insert_one(document_doc)
                return str(result.inserted_id)
            else:
                # Use local file storage instead
                return Document._create_local(document_doc)
        except Exception as e:
            print(f"Error creating document: {str(e)}")
            traceback.print_exc()
            # Fallback to local storage
            return Document._create_local(document_doc)
    
    @staticmethod
    def _create_local(document_doc):
        """Create a local document file when MongoDB is unavailable"""
        # Generate a simple UUID-like ID
        import uuid
        doc_id = str(uuid.uuid4())
        document_doc["_id"] = doc_id
        
        # Create documents directory if it doesn't exist
        docs_dir = os.path.join(LOCAL_STORAGE_DIR, 'documents')
        os.makedirs(docs_dir, exist_ok=True)
        
        # Save document to JSON file
        doc_path = os.path.join(docs_dir, f"{doc_id}.json")
        with open(doc_path, 'w') as f:
            # Store a shortened version of content if it's very large
            if len(document_doc["content"]) > 10000:
                print(f"Content is large ({len(document_doc['content'])} chars), storing first 10000 chars in local storage")
                full_content = document_doc["content"]
                document_doc["content"] = full_content[:10000] + "... [truncated for storage]"
                document_doc["content_truncated"] = True
                
                # Store full content in separate file
                content_path = os.path.join(docs_dir, f"{doc_id}_full_content.txt")
                with open(content_path, 'w') as cf:
                    cf.write(full_content)
            
            json.dump(document_doc, f, indent=2)
        
        print(f"Document saved locally with ID: {doc_id}")
        return doc_id
    
    @staticmethod
    def get_by_id(document_id):
        """Get a document by ID"""
        try:
            if MONGODB_CONNECTED:
                document = documents_collection.find_one({"_id": ObjectId(document_id)})
                return document
            else:
                return Document._get_local_by_id(document_id)
        except Exception as e:
            print(f"Error retrieving document: {str(e)}")
            # Try local storage as fallback
            return Document._get_local_by_id(document_id)
    
    @staticmethod
    def _get_local_by_id(document_id):
        """Get a document from local storage"""
        doc_path = os.path.join(LOCAL_STORAGE_DIR, 'documents', f"{document_id}.json")
        
        if not os.path.exists(doc_path):
            return None
            
        with open(doc_path, 'r') as f:
            document = json.load(f)
            
        # Check if content was truncated and load full content if available
        if document.get("content_truncated", False):
            content_path = os.path.join(LOCAL_STORAGE_DIR, 'documents', f"{document_id}_full_content.txt")
            if os.path.exists(content_path):
                with open(content_path, 'r') as cf:
                    document["content"] = cf.read()
                    document["content_truncated"] = False
        
        return document
    
    @staticmethod
    def get_all():
        """Get all documents"""
        try:
            if MONGODB_CONNECTED:
                return list(documents_collection.find())
            else:
                return Document._get_all_local()
        except Exception as e:
            print(f"Error retrieving all documents: {str(e)}")
            # Try local storage as fallback
            return Document._get_all_local()
            
    @staticmethod
    def _get_all_local():
        """Get all documents from local storage"""
        docs_dir = os.path.join(LOCAL_STORAGE_DIR, 'documents')
        
        if not os.path.exists(docs_dir):
            return []
            
        documents = []
        for filename in os.listdir(docs_dir):
            if filename.endswith('.json') and not filename.endswith('_full_content.json'):
                with open(os.path.join(docs_dir, filename), 'r') as f:
                    document = json.load(f)
                    documents.append(document)
        
        return documents


class Context:
    """Model for context parameters templates"""
    
    @staticmethod
    def create(name, description, parameters):
        """Create a new context template"""
        context_doc = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = contexts_collection.insert_one(context_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all():
        """Get all context templates"""
        return list(contexts_collection.find())
    
    @staticmethod
    def get_by_name(name):
        """Get a context template by name"""
        return contexts_collection.find_one({"name": name})
    
    @staticmethod
    def get_by_id(context_id):
        """Get a context template by ID"""
        return contexts_collection.find_one({"_id": ObjectId(context_id)})
    
    @staticmethod
    def update(context_id, name=None, description=None, parameters=None):
        """Update a context template"""
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if name is not None:
            update_data["name"] = name
            
        if description is not None:
            update_data["description"] = description
            
        if parameters is not None:
            update_data["parameters"] = parameters
            
        contexts_collection.update_one(
            {"_id": ObjectId(context_id)},
            {"$set": update_data}
        ) 
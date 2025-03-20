from flask import Blueprint, request, jsonify
from app.services.graph_service import GraphService
from app.services.ocr_service import MistralOCRService
from app.services.embeddings_service import EmbeddingsService
from app.services.node_chat_service import NodeChatService
from app.models.db_models import Query, Document, Context, Graph
import os
import json

# Create Blueprint
api = Blueprint('api', __name__)

# Initialize services
graph_service = GraphService()
ocr_service = MistralOCRService()
embeddings_service = EmbeddingsService()
node_chat_service = NodeChatService()

@api.route('/query', methods=['POST'])
def submit_query():
    """
    Submit a new query for graph generation
    
    Example request:
    ```
    {
        "query": "What is the St. Gallen Management Model?",
        "context_params": {
            "document_id": "67dbac15ea53f25878bfa9fd",
            "company": {
                "size": "medium",
                "maturity": "growth",
                "industry": "technology"
            },
            "management_role": "middle_management",
            "challenge_type": "organizational_restructuring",
            "environment": {
                "market_volatility": "high",
                "competitive_pressure": "medium",
                "regulatory_environment": "strict"
            }
        }
    }
    ```
    
    Context parameters help tailor the response to specific organizational contexts.
    All context parameters are optional.
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or "query" not in data:
            return jsonify({"error": "Invalid request, 'query' is required"}), 400
            
        # Extract data
        query_text = data["query"]
        user_id = data.get("user_id", "anonymous")
        context_params = data.get("context_params", {})
        
        graph_service = GraphService()
        
        # Generate graph for query
        query_id, graph_id = graph_service.generate_graph_for_query(user_id, query_text, context_params)
        
        if not graph_id:
            return jsonify({
                "error": "Failed to generate graph",
                "query_id": query_id
            }), 500
            
        # Return success response
        return jsonify({
            "success": True,
            "query_id": query_id,
            "graph_id": graph_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/query/<query_id>', methods=['GET'])
def get_query(query_id):
    """Get query details by ID"""
    try:
        query = Query.get_by_id(query_id)
        if not query:
            return jsonify({"error": "Query not found"}), 404
            
        # Convert to serializable format
        query_data = {
            "id": str(query["_id"]),
            "user_id": query["user_id"],
            "query_text": query["query_text"],
            "timestamp": query["timestamp"].isoformat(),
            "status": query["status"],
            "context_params": query.get("context_params", {})
        }
        
        if "graph_id" in query:
            query_data["graph_id"] = query["graph_id"]
            
        return jsonify(query_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/graph/<graph_id>', methods=['GET'])
def get_graph(graph_id):
    """Get graph data by ID"""
    try:
        # Get optional query parameters
        layer = request.args.get('layer', None)
        include_connections = request.args.get('connections', 'false').lower() == 'true'
        
        if include_connections:
            # Get graph with connections
            result = graph_service.get_graph_with_connections(graph_id)
        elif layer is not None:
            # Get graph filtered by layer
            result = graph_service.get_graph_by_layer(graph_id, int(layer))
        else:
            # Get full graph
            result = graph_service.get_graph(graph_id)
            
        if not result:
            return jsonify({"error": "Graph not found"}), 404
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/graph/<graph_id>/filter', methods=['POST'])
def filter_graph(graph_id):
    """Filter graph by context parameters"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Context parameters are required"}), 400
            
        context_params = data.get('context_params', {})
        
        filtered_graph = graph_service.get_filtered_graph(graph_id, context_params)
        
        if not filtered_graph:
            return jsonify({"error": "Graph not found or could not be filtered"}), 404
            
        return jsonify(filtered_graph), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/node/<graph_id>/<node_id>', methods=['GET'])
def get_node(graph_id, node_id):
    """Get details for a specific node in a graph"""
    try:
        graph_data = graph_service.get_graph(graph_id)
        if not graph_data:
            return jsonify({"error": "Graph not found"}), 404
            
        node_details = graph_service.extract_node_details(graph_data, node_id)
        if not node_details:
            return jsonify({"error": "Node not found"}), 404
            
        # Check if connections should be included
        include_connections = request.args.get('connections', 'false').lower() == 'true'
        
        if include_connections:
            # Get connections for this node
            connections = graph_service.get_node_connections(graph_id, node_id)
            node_details["connections"] = connections
            
        return jsonify(node_details), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/connections/<graph_id>', methods=['GET'])
def get_connections(graph_id):
    """Get all connections for a graph"""
    try:
        connections = Graph.get_connections(graph_id)
        
        if connections is None:
            return jsonify({"error": "Graph not found or no connections available"}), 404
            
        return jsonify(connections), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/connections/<graph_id>/<node_id>', methods=['GET'])
def get_node_connections(graph_id, node_id):
    """Get connections for a specific node"""
    try:
        connections = graph_service.get_node_connections(graph_id, node_id)
        
        return jsonify(connections), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/document', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
            
        # Get document metadata
        title = request.form.get('title', 'Untitled Document')
        metadata = {}
        
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except:
                pass
        
        # Save file temporarily
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        # Process document
        document_id = ocr_service.process_document(file_path, title, metadata)
        
        # Clean up
        os.remove(file_path)
        
        if not document_id:
            return jsonify({"error": "Failed to process document"}), 500
            
        # Process document for embeddings
        embedding_success = embeddings_service.process_document(document_id)
        
        # Return success response
        return jsonify({
            "success": True,
            "document_id": document_id,
            "embeddings_processed": embedding_success
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/documents', methods=['GET'])
def get_documents():
    """Get list of all documents"""
    try:
        documents = Document.get_all()
        
        # Convert to serializable format
        document_list = []
        for doc in documents:
            # Handle the case where created_at is already a string
            created_at = doc["created_at"]
            if not isinstance(created_at, str):
                created_at = created_at.isoformat()
            
            document_list.append({
                "id": str(doc["_id"]),
                "title": doc["title"],
                "created_at": created_at,
                "metadata": doc["metadata"]
            })
            
        return jsonify(document_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/context-templates', methods=['GET'])
def get_context_templates():
    """Get list of all context templates"""
    try:
        templates = Context.get_all()
        
        # Convert to serializable format
        template_list = []
        for template in templates:
            template_list.append({
                "id": str(template["_id"]),
                "name": template["name"],
                "description": template["description"],
                "parameters": template["parameters"]
            })
            
        return jsonify(template_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/context-templates', methods=['POST'])
def create_context_template():
    """Create a new context template"""
    try:
        data = request.json
        if not data or 'name' not in data or 'parameters' not in data:
            return jsonify({"error": "Name and parameters are required"}), 400
            
        name = data['name']
        description = data.get('description', '')
        parameters = data['parameters']
        
        template_id = Context.create(name, description, parameters)
        
        return jsonify({
            "success": True,
            "template_id": template_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/user/<user_id>/queries', methods=['GET'])
def get_user_queries(user_id):
    """Get recent queries for a user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        queries = Query.get_user_queries(user_id, limit)
        
        # Convert to serializable format
        query_list = []
        for query in queries:
            query_data = {
                "id": str(query["_id"]),
                "query_text": query["query_text"],
                "timestamp": query["timestamp"].isoformat(),
                "status": query["status"],
                "context_params": query.get("context_params", {})
            }
            
            if "graph_id" in query:
                query_data["graph_id"] = query["graph_id"]
                
            query_list.append(query_data)
            
        return jsonify(query_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/node-chat', methods=['POST'])
def node_chat():
    """
    Chat with a specific node to get more information about the concept
    
    Example request:
    ```
    {
        "node_id": "node_12",
        "graph_id": "67dbbafc3b11728551f5ce4c",
        "query": "How does this concept apply to healthcare organizations?",
        "document_id": "67dbac15ea53f25878bfa9fd",
        "chat_history": [
            {"role": "user", "content": "Can you explain this concept in simpler terms?"},
            {"role": "assistant", "content": "This concept refers to how organizations structure their decision-making processes..."}
        ]
    }
    ```
    
    The chat_history field is optional.
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['node_id', 'graph_id', 'query', 'document_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                "error": "Invalid request",
                "message": f"Required fields: {', '.join(required_fields)}"
            }), 400
            
        # Extract data
        node_id = data['node_id']
        graph_id = data['graph_id']
        query = data['query']
        document_id = data['document_id']
        chat_history = data.get('chat_history', [])
        
        # Generate response
        result = node_chat_service.generate_chat_response(
            graph_id, 
            node_id, 
            query, 
            document_id, 
            chat_history
        )
        
        # Check if there was an error
        if isinstance(result, tuple) and len(result) == 2 and "error" in result[0]:
            return jsonify(result[0]), result[1]
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
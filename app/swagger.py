from flask import jsonify

def get_swagger_spec():
    """Returns the Swagger specification for the API"""
    spec = {
        "swagger": "2.0",
        "info": {
            "title": "St. Gallen Management Model API",
            "description": "API for querying and exploring the St. Gallen Management Model with context-aware knowledge graphs",
            "version": "1.0.0"
        },
        "basePath": "/api",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {
            "/query": {
                "post": {
                    "summary": "Submit a query for graph generation",
                    "description": "Processes a query against the St. Gallen Management Model and generates a knowledge graph with context-specific insights",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "$ref": "#/definitions/QueryRequest"
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Query successfully submitted",
                            "schema": {
                                "$ref": "#/definitions/QueryResponse"
                            }
                        },
                        "400": {
                            "description": "Invalid request format"
                        },
                        "500": {
                            "description": "Server error"
                        }
                    }
                }
            },
            "/query/{query_id}": {
                "get": {
                    "summary": "Get query details",
                    "description": "Retrieves the details and status of a previously submitted query",
                    "parameters": [
                        {
                            "name": "query_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the query"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Query details",
                            "schema": {
                                "$ref": "#/definitions/QueryDetails"
                            }
                        },
                        "404": {
                            "description": "Query not found"
                        }
                    }
                }
            },
            "/graph/{graph_id}": {
                "get": {
                    "summary": "Get graph data",
                    "description": "Retrieves the knowledge graph generated for a query",
                    "parameters": [
                        {
                            "name": "graph_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the graph"
                        },
                        {
                            "name": "layer",
                            "in": "query",
                            "required": False,
                            "type": "integer",
                            "description": "Filter graph by layer (0-4)"
                        },
                        {
                            "name": "connections",
                            "in": "query",
                            "required": False,
                            "type": "boolean",
                            "description": "Include non-hierarchical connections between nodes"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Graph data",
                            "schema": {
                                "$ref": "#/definitions/Graph"
                            }
                        },
                        "404": {
                            "description": "Graph not found"
                        }
                    }
                }
            },
            "/graph/{graph_id}/filter": {
                "post": {
                    "summary": "Filter graph by context parameters",
                    "description": "Apply context-based filtering to a knowledge graph",
                    "parameters": [
                        {
                            "name": "graph_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the graph"
                        },
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "$ref": "#/definitions/FilterRequest"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Filtered graph data",
                            "schema": {
                                "$ref": "#/definitions/Graph"
                            }
                        },
                        "404": {
                            "description": "Graph not found"
                        }
                    }
                }
            },
            "/node/{graph_id}/{node_id}": {
                "get": {
                    "summary": "Get node details",
                    "description": "Retrieves detailed information about a specific node in a knowledge graph",
                    "parameters": [
                        {
                            "name": "graph_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the graph"
                        },
                        {
                            "name": "node_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the node"
                        },
                        {
                            "name": "connections",
                            "in": "query",
                            "required": False,
                            "type": "boolean",
                            "description": "Include connections for this node"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Node details",
                            "schema": {
                                "$ref": "#/definitions/Node"
                            }
                        },
                        "404": {
                            "description": "Node or graph not found"
                        }
                    }
                }
            },
            "/connections/{graph_id}": {
                "get": {
                    "summary": "Get all connections for a graph",
                    "description": "Retrieves all non-hierarchical connections between nodes in a graph",
                    "parameters": [
                        {
                            "name": "graph_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the graph"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of connections",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Connection"
                                }
                            }
                        },
                        "404": {
                            "description": "Graph not found or no connections available"
                        }
                    }
                }
            },
            "/connections/{graph_id}/{node_id}": {
                "get": {
                    "summary": "Get connections for a specific node",
                    "description": "Retrieves all connections involving a specific node",
                    "parameters": [
                        {
                            "name": "graph_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the graph"
                        },
                        {
                            "name": "node_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the node"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of node connections",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Connection"
                                }
                            }
                        }
                    }
                }
            },
            "/document": {
                "post": {
                    "summary": "Upload and process a document",
                    "description": "Uploads a PDF document, extracts text, and generates embeddings for querying",
                    "consumes": ["multipart/form-data"],
                    "parameters": [
                        {
                            "name": "file",
                            "in": "formData",
                            "required": True,
                            "type": "file",
                            "description": "PDF file to upload"
                        },
                        {
                            "name": "title",
                            "in": "formData",
                            "required": False,
                            "type": "string",
                            "description": "Document title"
                        },
                        {
                            "name": "metadata",
                            "in": "formData",
                            "required": False,
                            "type": "string",
                            "description": "JSON string with document metadata"
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Document successfully processed",
                            "schema": {
                                "$ref": "#/definitions/DocumentResponse"
                            }
                        },
                        "400": {
                            "description": "Invalid request format or file type"
                        },
                        "500": {
                            "description": "Server error"
                        }
                    }
                }
            },
            "/documents": {
                "get": {
                    "summary": "Get list of all documents",
                    "description": "Retrieves a list of all documents available for querying",
                    "responses": {
                        "200": {
                            "description": "List of documents",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Document"
                                }
                            }
                        }
                    }
                }
            },
            "/context-templates": {
                "get": {
                    "summary": "Get list of all context templates",
                    "description": "Retrieves predefined context templates for query enrichment",
                    "responses": {
                        "200": {
                            "description": "List of context templates",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/ContextTemplate"
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Create a new context template",
                    "description": "Creates a new predefined context template",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "$ref": "#/definitions/ContextTemplateRequest"
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Context template created",
                            "schema": {
                                "$ref": "#/definitions/ContextTemplateResponse"
                            }
                        },
                        "400": {
                            "description": "Invalid request format"
                        }
                    }
                }
            },
            "/user/{user_id}/queries": {
                "get": {
                    "summary": "Get recent queries for a user",
                    "description": "Retrieves the most recent queries submitted by a specific user",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "type": "integer",
                            "description": "Maximum number of queries to return"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of queries",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/QueryDetails"
                                }
                            }
                        }
                    }
                }
            },
            "/node-chat": {
                "post": {
                    "tags": ["Node Interaction"],
                    "summary": "Chat with a specific node",
                    "description": "Enables contextual conversations about specific nodes in the knowledge graph",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "$ref": "#/definitions/NodeChatRequest"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Chat response",
                            "schema": {
                                "$ref": "#/definitions/NodeChatResponse"
                            }
                        },
                        "400": {
                            "description": "Invalid request format"
                        },
                        "404": {
                            "description": "Node or graph not found"
                        },
                        "500": {
                            "description": "Server error"
                        }
                    }
                }
            }
        },
        "definitions": {
            "QueryRequest": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query text about the St. Gallen Management Model",
                        "example": "How can I apply the St. Gallen Management Model in my organization?"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Identifier for the user (defaults to 'anonymous')",
                        "example": "user123"
                    },
                    "context_params": {
                        "type": "object",
                        "description": "Additional context parameters to tailor the response",
                        "properties": {
                            "document_id": {
                                "type": "string",
                                "description": "ID of the document to query against",
                                "example": "67dbac15ea53f25878bfa9fd"
                            },
                            "company": {
                                "type": "object",
                                "description": "Company attributes",
                                "properties": {
                                    "size": {
                                        "type": "string",
                                        "enum": ["small", "medium", "large", "enterprise"],
                                        "example": "small"
                                    },
                                    "maturity": {
                                        "type": "string",
                                        "enum": ["startup", "growth", "mature", "declining"],
                                        "example": "startup"
                                    },
                                    "industry": {
                                        "type": "string",
                                        "example": "technology"
                                    }
                                }
                            },
                            "management_role": {
                                "type": "string",
                                "description": "Role of the person asking the question",
                                "enum": ["founder", "c_level", "middle_management", "team_lead", "consultant"],
                                "example": "founder"
                            },
                            "challenge_type": {
                                "type": "string",
                                "description": "Type of business challenge being faced",
                                "enum": ["growth", "efficiency", "innovation", "organizational_restructuring", "digital_transformation"],
                                "example": "growth"
                            },
                            "environment": {
                                "type": "object",
                                "description": "Environmental factors",
                                "properties": {
                                    "market_volatility": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high"],
                                        "example": "high"
                                    },
                                    "competitive_pressure": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high"],
                                        "example": "high"
                                    },
                                    "regulatory_environment": {
                                        "type": "string",
                                        "enum": ["relaxed", "moderate", "strict"],
                                        "example": "moderate"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "QueryResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "query_id": {
                        "type": "string",
                        "example": "67dbb7e4e16c33a1dc67a8ae"
                    },
                    "graph_id": {
                        "type": "string",
                        "example": "67dbb7f5e16c33a1dc67a8af"
                    }
                }
            },
            "QueryDetails": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "67dbb7e4e16c33a1dc67a8ae"
                    },
                    "user_id": {
                        "type": "string",
                        "example": "anonymous"
                    },
                    "query_text": {
                        "type": "string",
                        "example": "How can I apply the St. Gallen Management Model in my organization?"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2025-03-20T06:12:32.102000"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["processing", "completed", "failed"],
                        "example": "completed"
                    },
                    "context_params": {
                        "type": "object",
                        "example": {
                            "document_id": "67dbac15ea53f25878bfa9fd",
                            "company": {
                                "size": "small",
                                "maturity": "startup",
                                "industry": "technology"
                            }
                        }
                    },
                    "graph_id": {
                        "type": "string",
                        "example": "67dbb7f5e16c33a1dc67a8af"
                    }
                }
            },
            "Graph": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "node_0"
                    },
                    "title": {
                        "type": "string",
                        "example": "Applying SGMM in Startups"
                    },
                    "description": {
                        "type": "string",
                        "example": "Utilize the St. Gallen Management Model to navigate growth challenges in a small technology startup."
                    },
                    "layer": {
                        "type": "integer",
                        "example": 0
                    },
                    "relevance": {
                        "type": "integer",
                        "example": 10
                    },
                    "children": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Node"
                        }
                    }
                }
            },
            "Node": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "node_1"
                    },
                    "title": {
                        "type": "string",
                        "example": "Environment"
                    },
                    "description": {
                        "type": "string",
                        "example": "Understanding and adapting to external factors affecting the organization."
                    },
                    "layer": {
                        "type": "integer",
                        "example": 1
                    },
                    "relevance": {
                        "type": "integer",
                        "example": 9
                    },
                    "children": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Node"
                        }
                    },
                    "examples": {
                        "type": "array",
                        "description": "Real-world examples of the concept",
                        "items": {
                            "$ref": "#/definitions/Example"
                        }
                    }
                }
            },
            "Connection": {
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "example": "node_1"
                    },
                    "target_id": {
                        "type": "string",
                        "example": "node_5"
                    },
                    "relationship_type": {
                        "type": "string",
                        "example": "influences"
                    },
                    "description": {
                        "type": "string",
                        "example": "Environmental factors influence technological decisions"
                    },
                    "strength": {
                        "type": "integer",
                        "example": 4
                    }
                }
            },
            "FilterRequest": {
                "type": "object",
                "properties": {
                    "context_params": {
                        "type": "object",
                        "properties": {
                            "relevance_threshold": {
                                "type": "integer",
                                "description": "Minimum relevance score (1-10) for nodes to include",
                                "example": 7
                            },
                            "focus_area": {
                                "type": "string",
                                "description": "Area to focus on (e.g., 'strategy', 'structure')",
                                "example": "strategy"
                            }
                        }
                    }
                }
            },
            "Document": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "67dbac15ea53f25878bfa9fd"
                    },
                    "title": {
                        "type": "string",
                        "example": "St. Gallen Management Model"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2025-03-20T05:48:05.563515"
                    },
                    "metadata": {
                        "type": "object",
                        "example": {
                            "author": "SGMM",
                            "file_name": "sgmm.pdf",
                            "file_type": ".pdf",
                            "source": "Imported Book"
                        }
                    }
                }
            },
            "DocumentResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "document_id": {
                        "type": "string",
                        "example": "67dbac15ea53f25878bfa9fd"
                    },
                    "embeddings_processed": {
                        "type": "boolean",
                        "example": True
                    }
                }
            },
            "ContextTemplate": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "67dbc123ea53f25878bfa123"
                    },
                    "name": {
                        "type": "string",
                        "example": "Tech Startup Template"
                    },
                    "description": {
                        "type": "string",
                        "example": "Context template for technology startups"
                    },
                    "parameters": {
                        "type": "object",
                        "example": {
                            "company": {
                                "size": "small",
                                "maturity": "startup",
                                "industry": "technology"
                            },
                            "challenge_type": "growth",
                            "environment": {
                                "market_volatility": "high",
                                "competitive_pressure": "high"
                            }
                        }
                    }
                }
            },
            "ContextTemplateRequest": {
                "type": "object",
                "required": ["name", "parameters"],
                "properties": {
                    "name": {
                        "type": "string",
                        "example": "Tech Startup Template"
                    },
                    "description": {
                        "type": "string",
                        "example": "Context template for technology startups"
                    },
                    "parameters": {
                        "type": "object",
                        "example": {
                            "company": {
                                "size": "small",
                                "maturity": "startup",
                                "industry": "technology"
                            }
                        }
                    }
                }
            },
            "ContextTemplateResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "template_id": {
                        "type": "string",
                        "example": "67dbc123ea53f25878bfa123"
                    }
                }
            },
            "NodeChatRequest": {
                "type": "object",
                "required": ["node_id", "graph_id", "query", "document_id"],
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "ID of the node to chat about",
                        "example": "node_12"
                    },
                    "graph_id": {
                        "type": "string",
                        "description": "ID of the graph containing the node",
                        "example": "67dbbafc3b11728551f5ce4c"
                    },
                    "query": {
                        "type": "string",
                        "description": "User's question about the node",
                        "example": "How does this concept apply to healthcare organizations?"
                    },
                    "document_id": {
                        "type": "string",
                        "description": "ID of the document to use for context",
                        "example": "67dbac15ea53f25878bfa9fd"
                    },
                    "chat_history": {
                        "type": "array",
                        "description": "Previous messages in the conversation (optional)",
                        "items": {
                            "$ref": "#/definitions/ChatMessage"
                        }
                    }
                }
            },
            "ChatMessage": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["user", "assistant"],
                        "description": "The role of the message sender",
                        "example": "user"
                    },
                    "content": {
                        "type": "string",
                        "description": "The message content",
                        "example": "Can you explain this concept in simpler terms?"
                    }
                }
            },
            "NodeChatResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "response": {
                        "type": "string",
                        "description": "The AI's response to the query",
                        "example": "In healthcare organizations, this strategic management concept helps with resource allocation and prioritization..."
                    },
                    "examples": {
                        "type": "array",
                        "description": "Real-world examples illustrating the concept",
                        "items": {
                            "$ref": "#/definitions/Example"
                        }
                    },
                    "related_nodes": {
                        "type": "array",
                        "description": "Related nodes that might be of interest",
                        "items": {
                            "$ref": "#/definitions/RelatedNode"
                        }
                    },
                    "suggested_questions": {
                        "type": "array",
                        "description": "Suggested follow-up questions",
                        "items": {
                            "type": "string"
                        },
                        "example": [
                            "How does this relate to change management?",
                            "What are the main challenges in implementing this?",
                            "Can you provide a comparison with traditional approaches?"
                        ]
                    }
                }
            },
            "Example": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the example",
                        "example": "Mayo Clinic's Implementation"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the example",
                        "example": "The Mayo Clinic applied this approach by restructuring their departments..."
                    }
                }
            },
            "RelatedNode": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID of the related node",
                        "example": "node_15"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the related node",
                        "example": "Healthcare Management"
                    },
                    "relevance": {
                        "type": "number",
                        "format": "float",
                        "description": "Relevance score (0-1)",
                        "example": 0.87
                    }
                }
            }
        }
    }
    
    return spec 
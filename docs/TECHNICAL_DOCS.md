# St. Gallen Management Model Application - Technical Documentation

## 1. Architecture Overview

The St. Gallen Management Model (SGMM) application is built as a modern, modular web service that leverages several technologies to provide an intelligent knowledge management system. The application follows a service-oriented architecture pattern with clear separation of concerns.

### 1.1 High-Level Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Client         │◄────►│  Flask API      │◄────►│  Services Layer │
│  Applications   │      │  Backend        │      │                 │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                         │
                                                         ▼
                          ┌─────────────────┐      ┌─────────────────┐
                          │                 │      │                 │
                          │  Vector Database│◄────►│  Document       │
                          │  (Weaviate)     │      │  Storage        │
                          │                 │      │                 │
                          └─────────────────┘      └─────────────────┘
                                  │
                                  ▼
                          ┌─────────────────┐
                          │                 │
                          │  MongoDB        │
                          │  (Data Storage) │
                          │                 │
                          └─────────────────┘
```

## 2. Technology Stack

### 2.1 Core Technologies

- **Backend Framework**: Flask (Python)
- **Database**: 
  - MongoDB (document storage, query tracking, graph data)
  - Weaviate (vector database for semantic search)
- **AI/ML Components**:
  - OpenAI API for LLM functionality
  - Text embeddings for semantic search
- **Containerization**: Docker and Docker Compose
- **Documentation**: Swagger/OpenAPI

### 2.2 Key Dependencies

- **Flask Ecosystem**:
  - Flask-CORS (for cross-origin resource sharing)
  - Flask-Swagger-UI (for API documentation)
- **Data Processing**:
  - PyPDF2 (PDF processing)
  - OCR libraries for document extraction
  - Regular expressions for text processing
- **AI/ML Integration**:
  - OpenAI Python client
  - Vector similarity search

## 3. Core Components

### 3.1 API Layer (`app/routes/`)

The API layer exposes HTTP endpoints for client applications to interact with the system:

- **API Blueprint** (`app/routes/api.py`): Main API routes
- **Swagger** (`app/routes/swagger.py`): API documentation endpoints

### 3.2 Services Layer (`app/services/`)

The services layer implements the core business logic:

- **EmbeddingsService**: Handles vector embeddings and semantic search
- **GraphService**: Manages knowledge graph operations
- **RAGService**: Implements Retrieval-Augmented Generation
- **OCRService**: Handles document scanning and text extraction
- **NodeChatService**: Provides interactive chat functionality for graph nodes

### 3.3 Data Layer (`app/models/`)

The data layer handles database operations and defines data structures:

- **DB Models**: MongoDB document schemas
- **Request/Response Models**: Data validation and serialization

### 3.4 Utilities (`app/utils/`)

Support functions and initialization scripts:

- **Import Book**: Utility for importing textbooks
- **Database Initialization**: Setup scripts for initial data
- **Text Processing**: Helper functions for working with text

## 4. Data Flow

### 4.1 Document Processing Pipeline

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐
│          │    │          │    │           │    │           │
│  Upload  │───►│  OCR     │───►│  Chunking │───►│  Embedding│
│  PDF     │    │  Process │    │           │    │  Creation │
│          │    │          │    │           │    │           │
└──────────┘    └──────────┘    └───────────┘    └───────────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │               │
                                              │  Vector Store │
                                              │  Indexing     │
                                              │               │
                                              └───────────────┘
```

1. Documents (PDFs) are uploaded to the system
2. OCR processing extracts text from the documents
3. Text is chunked into manageable segments
4. Embeddings are created for each chunk
5. Embeddings are indexed in the vector database

### 4.2 Query Processing Pipeline

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐
│          │    │          │    │           │    │           │
│  User    │───►│  Context │───►│  Retrieval│───►│  Graph    │
│  Query   │    │  Enrichment   │  (RAG)    │    │  Generation│
│          │    │          │    │           │    │           │
└──────────┘    └──────────┘    └───────────┘    └───────────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │               │
                                              │  Response     │
                                              │  Delivery     │
                                              │               │
                                              └───────────────┘
```

1. User submits a query with context parameters
2. Query is enriched with contextual information
3. Relevant information is retrieved using RAG
4. Knowledge graph is generated based on retrieved information
5. Response is delivered to the user

### 4.3 Node Chat Flow

```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    
│          │    │              │    │               │    
│  Node    │───►│  Document    │───►│  Response     │    
│  Query   │    │  Retrieval   │    │  Generation   │    
│          │    │              │    │               │    
└──────────┘    └──────────────┘    └───────────────┘    
                                           │
                                           ▼
                                    ┌─────────────────┐
                                    │                 │
                                    │  Examples &     │
                                    │  Suggestions    │
                                    │                 │
                                    └─────────────────┘
```

1. User submits a query about a specific node
2. Relevant document context is retrieved
3. LLM generates a response with the context
4. Examples, related nodes, and suggested questions are extracted
5. Complete response is returned to the user

## 5. Implementation Details

### 5.1 Knowledge Graph Structure

The system generates hierarchical knowledge graphs with the following structure:

- **Root Node (Layer 0)**: Main topic or query focus
- **Primary Concepts (Layer 1)**: Key concepts from the management model
- **Secondary Concepts (Layer 2)**: Detailed aspects of primary concepts
- **Tertiary Elements (Layer 3+)**: Implementation details and examples

Nodes contain:
- Unique identifier
- Title and description
- Layer information
- Relevance score
- Connections to other nodes

### 5.2 Context Enrichment

The system enriches queries with organizational context:

- Company attributes (size, maturity, industry)
- Management role
- Challenge type
- Environmental factors

These parameters influence the content and structure of generated knowledge graphs, making them more relevant to specific organizational contexts.

### 5.3 Retrieval-Augmented Generation (RAG)

The RAG implementation follows these steps:

1. Query embedding generation
2. Semantic search in the vector database
3. Retrieval of relevant document chunks
4. Context assembly with relevant passages
5. Prompt construction with query and context
6. LLM generation of structured response

### 5.4 Node Chat Implementation

The NodeChatService handles interactive conversations about graph nodes:

1. Node detail retrieval from the graph
2. Context assembly with node information
3. Document context retrieval using semantic search
4. Response generation using the LLM
5. Post-processing to extract examples and suggestions
6. Response formatting and delivery

### 5.5 Text Embeddings

The system uses OpenAI's embedding models to convert text into high-dimensional vectors, which are then stored in Weaviate for efficient semantic search. The implementation includes:

- Chunking strategies for optimal semantic representation
- Embedding generation for documents and queries
- Vector similarity search for retrieval
- Dynamic weighting based on relevance scores

## 6. Deployment Architecture

### 6.1 Docker Container Structure

The application is containerized using Docker with the following components:

- **sgmm-app**: Flask application container
- **mongodb**: Database container for document storage
- **weaviate**: Vector database container for embeddings
- **init-db**: Initialization container for database setup

### 6.2 Environment Configuration

The application uses environment variables for configuration:

- API keys for external services (OpenAI, Mistral)
- Database connection parameters
- Model configuration (embedding model, LLM model)
- Text processing parameters (chunk size, overlap)

### 6.3 Volume Management

The application manages several data volumes:

- **mongodb_data**: Persistent MongoDB storage
- **weaviate_data**: Persistent vector database storage
- **uploads**: Temporary storage for uploaded files
- **books**: Volume for PDF textbook storage

## 7. Security Considerations

The current implementation has basic security features designed for local development:

- API keys for external services
- Basic error handling to prevent information leakage
- Input validation to prevent injection attacks

For production deployment, additional security measures would be necessary:

- User authentication and authorization
- HTTPS encryption
- Rate limiting
- More comprehensive input validation
- Secure handling of API keys

## 8. Scaling Considerations

For scaling the application:

- Implement load balancing for the Flask application
- Use MongoDB replication for database redundancy
- Implement caching for frequently accessed data
- Optimize embedding storage and retrieval
- Consider distributed processing for document ingestion

## 9. Monitoring and Maintenance

To ensure system health and performance:

- Implement logging throughout the application
- Set up monitoring for API performance
- Track resource usage (memory, CPU, storage)
- Monitor external API usage and costs
- Implement alerting for critical failures 
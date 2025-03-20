# St. Gallen Management Model - Current Deployment Architecture

This document describes the current implementation of the St. Gallen Management Model (SGMM) application, explaining how it's currently configured in the development environment and the architectural decisions behind its design.

## 1. Current Architecture

The SGMM application is built using a containerized microservices approach with the following components:

```
┌────────────────────────────────────────────────────────────────┐
│                     Current Environment                         │
│                                                                 │
│                      ┌─────────────┐                            │
│                      │             │                            │
│                      │  Flask App  │                            │
│                      │  Container  │                            │
│                      │             │                            │
│                      └─────────────┘                            │
│                            │                                    │
│                            ▼                                    │
│         ┌─────────────────────────────────────┐                │
│         │                                     │                 │
│         ▼                                     ▼                 │
│  ┌─────────────┐                      ┌─────────────┐          │
│  │             │                      │             │          │
│  │  MongoDB    │                      │  Weaviate   │          │
│  │  Container  │                      │  Container  │          │
│  │             │                      │             │          │
│  └─────────────┘                      └─────────────┘          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

The application currently uses:
- Flask (Python) for the API backend
- MongoDB for document storage and query tracking
- Weaviate as a vector database for semantic search
- Docker and Docker Compose for containerization

## 2. Current Implementation

### 2.1 Technology Choices

For the current implementation, I've made the following choices:

- **Backend Framework**: Flask was chosen for its simplicity and flexibility, making it easy to implement RESTful APIs.
- **Database**: 
  - MongoDB stores document metadata, graph structures, and query history
  - Weaviate stores vector embeddings for semantic search capabilities
- **AI/ML Integration**: The application uses OpenAI's API for LLM functionality and embeddings
- **Containerization**: Docker Compose for local development and testing

### 2.2 Current Environment Configuration

The application currently runs with these environment settings:

```
# API Keys
OPENAI_API_KEY=[active OpenAI key]
MISTRAL_API_KEY=[optional Mistral key]

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/
MONGODB_DB_NAME=sgmm_db
WEAVIATE_URL=http://weaviate:8080
WEAVIATE_API_KEY=

# Application Configuration
FLASK_DEBUG=1
SECRET_KEY=dev-key-change-in-production

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-large
LLM_MODEL=gpt-4o
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 2.3 Docker Compose Configuration

The current `docker-compose.yml` file defines the following services:

- **sgmm-app**: Flask application container exposing port 5001
- **mongodb**: MongoDB database for document storage
- **weaviate**: Vector database with authentication disabled for development
- **init-db**: One-time initialization service for database setup

The containers are configured with appropriate volumes for local development:
- `./app:/app/app` for live code changes
- `./uploads:/app/uploads` for document uploads
- `./books:/app/books` for textbook PDFs

## 3. How It Works Locally

### 3.1 Development Workflow

The current setup enables a smooth development workflow:

1. **Starting the Environment**: 
   ```bash
   docker-compose up -d
   ```
   This launches all services with the Flask app accessible at http://localhost:5001

2. **Code Changes**: 
   The app directory is mounted as a volume, so code changes take effect immediately with Flask's debug mode

3. **Document Processing**:
   - PDFs placed in the `books` directory can be imported
   - The system extracts text, chunks it, creates embeddings, and stores them in Weaviate
   - Current chunk size is set to 1000 tokens with 200 token overlap

4. **Query Processing**:
   - User queries are enhanced with context parameters
   - The system retrieves relevant document chunks via vector similarity search
   - The LLM generates knowledge graphs based on the retrieved content
   - Results are stored in MongoDB and returned to the user

### 3.2 Data Flow in the Current System

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐
│          │    │          │    │           │    │           │
│  User    │───►│  API     │───►│  Services │───►│  Database │
│  Request │    │  Endpoint│    │  Layer    │    │  Storage  │
│          │    │          │    │           │    │           │
└──────────┘    └──────────┘    └───────────┘    └───────────┘
                                      │
                                      ▼
                                ┌──────────────┐
                                │              │
                                │  LLM API     │
                                │  (OpenAI)    │
                                │              │
                                └──────────────┘
```

When a user interacts with the system:

1. Requests come in through Flask API endpoints
2. The service layer handles business logic
3. MongoDB stores structured data and query history
4. Weaviate provides vector search capabilities
5. OpenAI's API provides embeddings and LLM responses
6. Responses are formatted and returned to the user

### 3.3 Current Volume Management

The system uses several docker volumes for data persistence:

- **mongodb_data**: Stores MongoDB documents, collections, and indexes
- **weaviate_data**: Stores vector embeddings and schema information
- **./uploads**: Local directory mounted for user document uploads
- **./books**: Local directory mounted for textbook storage

## 4. Key Components

### 4.1 Core Services

The application is structured around several key services:

- **EmbeddingsService**: Handles vector embeddings creation and retrieval
- **GraphService**: Manages knowledge graph generation and manipulation
- **RAGService**: Implements Retrieval-Augmented Generation for knowledge graph creation
- **OCRService**: Extracts text from PDF documents
- **NodeChatService**: Provides interactive chat functionality for graph nodes

### 4.2 API Endpoints

The current implementation exposes these main API routes:

- **/api/query**: Submit queries for knowledge graph generation
- **/api/graph/{graph_id}**: Retrieve generated knowledge graphs
- **/api/node/{graph_id}/{node_id}**: Get detailed information about specific nodes
- **/api/document**: Upload and process PDF documents
- **/api/node-chat**: Interactive chat about specific graph nodes

### 4.3 Authentication and Security

In the current development setup:

- Authentication is disabled for local testing
- Weaviate's anonymous access is enabled
- MongoDB doesn't require authentication
- CORS is enabled to allow local frontend development

## 5. Development to Production Considerations

The current implementation is optimized for development. For production deployment, the following aspects would need attention:

### 5.1 Current Development Optimizations

- Debug mode is enabled for easier troubleshooting
- Live code reloading is configured via volume mounts
- External API keys are passed through from the host environment
- Services expose ports directly to the host for easy access

### 5.2 Resource Usage in Development

The current resource usage in development is:

- MongoDB: ~500MB RAM, minimal CPU
- Weaviate: ~1.5GB RAM, occasionally higher CPU during indexing
- Flask: ~200MB RAM, CPU varies with request load

### 5.3 Performance Characteristics

In the current implementation:

- Document processing takes about 5-10 minutes for a 300-page PDF
- Query processing typically takes 10-15 seconds
- Knowledge graph generation depends on query complexity (30-60 seconds)
- Node chat responses generate in approximately 5-10 seconds

## 6. Import Book Functionality

The application includes a custom utility for importing management textbooks:

```bash
# Currently used as:
docker-compose exec sgmm-app python -m app.utils.import_book /app/books/sgmm_textbook.pdf --title "St. Gallen Management Model" --author "Author Name"
```

This utility:
1. Extracts text from the PDF
2. Chunks the text into manageable segments
3. Creates embeddings for each chunk
4. Stores embeddings in Weaviate
5. Records document metadata in MongoDB

## 7. Current Limitations and Future Enhancements

The current implementation has some limitations that could be addressed in production:

- No authentication or user management system
- Limited error handling in some edge cases
- No dedicated caching mechanism for frequent queries
- Basic logging without structured log aggregation
- No metrics collection for system performance

## 8. External Dependencies and API Usage

The system currently relies on:

- **OpenAI API**: For embeddings and LLM responses
  - Currently using `text-embedding-3-large` and `gpt-4o`
  - API key passed through environment variables
  - Usage patterns vary based on application usage

- **Mistral API**: Configured as an optional alternative
  - Not actively used in current implementation
  
## 9. Testing the Current Setup

To verify the system is working correctly, I've been using these methods:

- API health check: `curl http://localhost:5001/`
- Interactive Swagger docs: `http://localhost:5001/api/docs`
- Example queries through Postman collections
- Book imports via command line 
- MongoDB inspection through Compass

## 10. Current Backup Approach

For development purposes, data persistence is handled through Docker volumes. Manual backups can be performed with:

- MongoDB data: Docker volume backup
- Weaviate data: Docker volume backup
- Document files: Direct copy from mounted directories 
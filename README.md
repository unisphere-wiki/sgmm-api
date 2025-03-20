# St. Gallen Management Model (SGMM) Application

A decision support application built on the St. Gallen Management Model that uses Retrieval Augmented Generation (RAG) to help managers make strategic decisions.

## Overview

This application allows managers to submit queries about strategic business decisions. The backend leverages a RAG engine to extract relevant insights from the St. Gallen Management Model and transforms them into a structured JSON graph. This graph presents a hierarchical view of decision factors organized by management domains.

The application components include:

- Flask REST API backend
- RAG engine using OpenAI embeddings and LLM
- PDF text extraction with fallback to Mistral OCR API when needed
- MongoDB for document and graph storage
- Weaviate vector database for semantic search

## Hierarchical Graph Structure

The application generates a layered hierarchical graph structure:

- **Layer 0**: Central node representing the main management topic or decision
- **Layer 1**: The 10,000ft view showing core elements of the St. Gallen Management Model
- **Layer 2**: Main management dimensions related to the query
- **Layer 3**: Specific concepts, theories, and methodologies
- **Layer 4**: Practical applications and case studies (when relevant)

The graph also includes cross-connections between nodes that have relationships beyond the hierarchical parent-child structure.

## Context Personalization

The application supports personalized content based on multiple dimensions:

- **Company Profile**: Size, maturity stage, industry, legal form
- **Management Role**: Management level, functional area, decision authority
- **Management Challenge**: Challenge type, timeframe, complexity
- **Environmental Context**: Market dynamics, technological intensity, regulatory density, global orientation

These parameters influence the relevance scores of different nodes in the graph, allowing for customized views based on specific organizational contexts.

## Project Structure

```
sgmm_app/
├── app/
│   ├── app.py               # Main Flask application
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   │   └── db_models.py     # MongoDB models
│   ├── routes/              # API routes
│   │   └── api.py           # REST API endpoints
│   ├── services/            # Business logic
│   │   ├── embeddings_service.py  # Text embeddings and vector search
│   │   ├── graph_service.py       # Decision graph generation
│   │   ├── ocr_service.py         # OCR processing with Mistral
│   │   └── rag_service.py         # RAG implementation
│   └── utils/               # Utility functions
│       └── init_db.py       # Database initialization
├── .env.example             # Environment variables template
├── README.md                # Documentation
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

## Documentation

Detailed documentation for the application is available in the `docs` folder:

- [API Documentation](docs/API_DOCS.md) - Complete API reference including endpoints, request/response examples
- [Technical Documentation](docs/TECHNICAL_DOCS.md) - Architecture overview, implementation details, and data flows
- [Deployment Guide](docs/DEPLOYMENT.md) - Current deployment architecture and considerations
- [Frontend Specifications](docs/FRONTEND_SPECS.md) - Frontend implementation details and UI components

## Setup Instructions

### Option 1: Docker Setup (Recommended)

The easiest way to run the application is using Docker and Docker Compose, which will set up all necessary services automatically.

#### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Mistral AI API key

#### Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd sgmm_app
   ```

2. Create a `.env` file from the template:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file to add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

4. Start the application stack:
   ```
   docker-compose up -d
   ```

The application will be available at http://localhost:5000 once all services are up. The database will be automatically initialized with sample data.

To stop the application:
```
docker-compose down
```

To view logs:
```
docker-compose logs -f
```

### Option 2: Manual Setup

### Prerequisites

- Python 3.7+
- MongoDB
- Weaviate vector database
- OpenAI API key
- Mistral AI API key
- Poppler (system dependency for pdf2image)
  - macOS: `brew install poppler`
  - Ubuntu: `apt-get install poppler-utils`
  - Windows: [Download binary](https://github.com/oschwartz10612/poppler-windows/releases/)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd sgmm_app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```
   
5. Edit the `.env` file with your API keys and configuration.

### Running the Application

1. Initialize the database with sample data:
   ```
   python -m app.utils.init_db
   ```

2. Start the application:
   ```
   python run.py
   ```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Query Management

- `POST /api/query`: Submit a new management decision query (supports context parameters)
- `GET /api/query/{query_id}`: Get details of a query
- `GET /api/user/{user_id}/queries`: Get a user's recent queries

### Graph Access

- `GET /api/graph/{graph_id}`: Get the complete decision graph
  - `?layer={0-4}`: Filter graph by layer
  - `?connections=true`: Include cross-connections
- `POST /api/graph/{graph_id}/filter`: Filter graph by context parameters
- `GET /api/node/{graph_id}/{node_id}`: Get details of a specific node
  - `?connections=true`: Include node connections
- `GET /api/connections/{graph_id}`: Get all connections for a graph
- `GET /api/connections/{graph_id}/{node_id}`: Get connections for a specific node

### Document Management

- `POST /api/document`: Upload and process a new document
- `GET /api/documents`: Get list of all documents

### Context Templates

- `GET /api/context-templates`: Get list of available context templates
- `POST /api/context-templates`: Create a new context template

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_API_KEY | OpenAI API key for embeddings and LLM | |
| MISTRAL_API_KEY | Mistral AI API key for OCR API | |
| WEAVIATE_URL | URL for Weaviate vector database | |
| WEAVIATE_API_KEY | API key for Weaviate | |
| MONGODB_URI | MongoDB connection URI | mongodb://localhost:27017/ |
| MONGODB_DB_NAME | MongoDB database name | sgmm_db |
| DEBUG | Enable debug mode | False |
| SECRET_KEY | Flask secret key | dev-key-change-in-production |
| PORT | Port to run the application | 5000 |
| EMBEDDING_MODEL | OpenAI embedding model | text-embedding-3-large |
| LLM_MODEL | OpenAI LLM model | gpt-4o |

## Document Processing

The application supports uploading PDF documents containing management textbook content. The system:

1. Extracts text directly from PDFs when possible using PyPDF2
2. Falls back to OCR processing with Mistral AI for scanned pages or images
3. Chunks the text and creates embeddings for semantic search
4. Uses the processed text to generate insights from user queries

## Importing Management Textbooks

There are several ways to import your St. Gallen Management Model textbook into the system:

### Option 1: Using the Import Script (Recommended)

The system includes a command-line utility for importing PDF books:

```bash
# When running without Docker
python -m app.utils.import_book path/to/your/textbook.pdf --title "St. Gallen Management Model" --author "Author Name" --year 2023

# When running with Docker
docker-compose exec sgmm-app python -m app.utils.import_book /app/books/textbook.pdf --title "St. Gallen Management Model" --author "Author Name" --year 2023
```

For Docker users, first copy your PDF to the books directory:
```bash
# Create a books directory if it doesn't exist
mkdir -p books

# Copy your PDF into it
cp path/to/your/textbook.pdf books/
```

### Option 2: Using the API Endpoint

You can use an API client like Postman or curl to upload your PDF:

```bash
curl -X POST http://localhost:5000/api/document \
  -F "file=@path/to/your/textbook.pdf" \
  -F "title=St. Gallen Management Model" \
  -F 'metadata={"author": "Author Name", "year": 2023}'
```

Note that the API endpoint has file size limitations and is better suited for smaller documents.

### After Importing

Once your book is imported, the system will:
1. Extract text from the PDF
2. Generate embeddings for semantic search
3. Make the content available for queries through the RAG system

You can verify the import was successful by checking the available documents:
```bash
# API endpoint
GET http://localhost:5000/api/documents

# Command line with Docker
docker-compose exec sgmm-app python -c "from app.models.db_models import Document; print(Document.get_all())"
```

## License

[MIT License](LICENSE)
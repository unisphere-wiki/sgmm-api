# St. Gallen Management Model API Documentation

This document provides comprehensive documentation for the St. Gallen Management Model (SGMM) API, allowing you to interact with contextual knowledge graphs based on management models.

## Base URL

```
http://localhost:5001/api
```

## Interactive Documentation

The API provides an interactive Swagger UI documentation at:

```
http://localhost:5001/api/docs
```

Use this interface to explore, understand, and test all API endpoints.

## Authentication

Currently, the API does not require authentication for local development. In a production environment, authentication mechanisms would be implemented.

## Core Endpoints

### Query Management

#### Submit a Query

Creates a new query to generate a knowledge graph based on the St. Gallen Management Model.

- **URL**: `/query`
- **Method**: `POST`
- **Request Body**:

```json
{
  "query": "How can I apply the St. Gallen Management Model in my organization?",
  "context_params": {
    "document_id": "67dbac15ea53f25878bfa9fd",
    "company": {
      "size": "small",
      "maturity": "startup",
      "industry": "technology"
    },
    "management_role": "founder",
    "challenge_type": "growth",
    "environment": {
      "market_volatility": "high",
      "competitive_pressure": "high"
    }
  }
}
```

- **Response**: `201 Created`

```json
{
  "success": true,
  "query_id": "67dbb7e4e16c33a1dc67a8ae",
  "graph_id": "67dbb7f5e16c33a1dc67a8af"
}
```

#### Get Query Status

Retrieves information about a previously submitted query.

- **URL**: `/query/{query_id}`
- **Method**: `GET`
- **Response**: `200 OK`

```json
{
  "id": "67dbb7e4e16c33a1dc67a8ae",
  "user_id": "anonymous",
  "query_text": "How can I apply the St. Gallen Management Model in my organization?",
  "timestamp": "2025-03-20T06:12:32.102000",
  "status": "completed",
  "context_params": {
    "document_id": "67dbac15ea53f25878bfa9fd",
    "company": {
      "size": "small",
      "maturity": "startup",
      "industry": "technology"
    }
  },
  "graph_id": "67dbb7f5e16c33a1dc67a8af"
}
```

### Knowledge Graph Endpoints

#### Get Graph Data

Retrieves the knowledge graph generated for a query.

- **URL**: `/graph/{graph_id}`
- **Method**: `GET`
- **Query Parameters**:
  - `layer` (optional): Filter by graph layer
  - `connections` (optional): Include non-hierarchical connections
- **Response**: `200 OK`

```json
{
  "id": "node_0",
  "title": "Applying SGMM in Startups",
  "description": "Utilize the St. Gallen Management Model to navigate growth challenges in a small technology startup facing high market volatility and competitive pressure.",
  "layer": 0,
  "relevance": 10,
  "children": [
    {
      "id": "node_1",
      "title": "Environment",
      "description": "Understand and adapt to the external factors affecting the organization, such as market volatility and competitive pressure.",
      "layer": 1,
      "relevance": 9,
      "children": [...]
    },
    ...
  ]
}
```

#### Filter Graph

Applies additional filtering to an existing graph.

- **URL**: `/graph/{graph_id}/filter`
- **Method**: `POST`
- **Request Body**:

```json
{
  "context_params": {
    "relevance_threshold": 7,
    "focus_area": "strategy"
  }
}
```

- **Response**: `200 OK` - Returns filtered graph with the same structure as the Get Graph response

#### Get Node Details

Retrieves detailed information about a specific node in a graph.

- **URL**: `/node/{graph_id}/{node_id}`
- **Method**: `GET`
- **Query Parameters**:
  - `connections` (optional): Include connections for this node
- **Response**: `200 OK`

```json
{
  "id": "node_1",
  "title": "Environment",
  "description": "Understanding and adapting to external factors affecting the organization.",
  "layer": 1,
  "relevance": 9,
  "children": [...]
}
```

### Document Management

#### Upload Document

Uploads and processes a PDF document for use with the system.

- **URL**: `/document`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Parameters**:
  - `file`: PDF file
  - `title` (optional): Document title
  - `metadata` (optional): JSON string with document metadata
- **Response**: `201 Created`

```json
{
  "success": true,
  "document_id": "67dbac15ea53f25878bfa9fd",
  "embeddings_processed": true
}
```

#### List Documents

Retrieves a list of all documents available for querying.

- **URL**: `/documents`
- **Method**: `GET`
- **Response**: `200 OK`

```json
[
  {
    "id": "67dbac15ea53f25878bfa9fd",
    "title": "St. Gallen Management Model",
    "created_at": "2025-03-20T05:48:05.563515",
    "metadata": {
      "author": "SGMM",
      "file_name": "sgmm.pdf",
      "file_type": ".pdf",
      "source": "Imported Book"
    }
  },
  ...
]
```

### Context Templates

#### List Context Templates

Retrieves predefined context templates for query enrichment.

- **URL**: `/context-templates`
- **Method**: `GET`
- **Response**: `200 OK`

```json
[
  {
    "id": "67dbc123ea53f25878bfa123",
    "name": "Tech Startup Template",
    "description": "Context template for technology startups",
    "parameters": {
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
  },
  ...
]
```

#### Create Context Template

Creates a new predefined context template.

- **URL**: `/context-templates`
- **Method**: `POST`
- **Request Body**:

```json
{
  "name": "Enterprise Digital Transformation",
  "description": "Template for digital transformation in large enterprises",
  "parameters": {
    "company": {
      "size": "enterprise",
      "maturity": "mature",
      "industry": "manufacturing"
    },
    "management_role": "c_level",
    "challenge_type": "digital_transformation",
    "environment": {
      "market_volatility": "medium",
      "competitive_pressure": "high",
      "regulatory_environment": "strict"
    }
  }
}
```

- **Response**: `201 Created`

```json
{
  "success": true,
  "template_id": "67dbc123ea53f25878bfa456"
}
```

## Node Interaction

### Node Chat

Enables interactive conversations about specific nodes in the knowledge graph.

- **URL**: `/node-chat`
- **Method**: `POST`
- **Request Body**:

```json
{
  "node_id": "node_12",
  "graph_id": "67dbbafc3b11728551f5ce4c",
  "query": "How does this concept apply to healthcare organizations?",
  "document_id": "67dbac15ea53f25878bfa9fd",
  "chat_history": [
    {
      "role": "user",
      "content": "Can you explain this concept in simpler terms?"
    },
    {
      "role": "assistant",
      "content": "This concept refers to how organizations structure their decision-making processes..."
    }
  ]
}
```

**Required Parameters:**
- `node_id`: ID of the node to chat about
- `graph_id`: ID of the graph containing the node
- `query`: User's question about the node
- `document_id`: ID of the document to use for context

**Optional Parameters:**
- `chat_history`: Previous messages in the conversation

- **Response**: `200 OK`

```json
{
  "success": true,
  "response": "In healthcare organizations, this strategic management concept helps with resource allocation and prioritization...",
  "examples": [
    {
      "title": "Mayo Clinic's Implementation",
      "description": "The Mayo Clinic applied this approach by..."
    },
    {
      "title": "Healthcare Startups",
      "description": "Emerging telemedicine companies have adapted this concept by..."
    }
  ],
  "related_nodes": [
    {
      "id": "node_15",
      "title": "Healthcare Management",
      "relevance": 0.87
    }
  ],
  "suggested_questions": [
    "How does this relate to change management?",
    "What are the main challenges in implementing this?",
    "Can you provide a comparison with traditional approaches?"
  ]
}
```

**Response Fields:**
- `success`: Boolean indicating success
- `response`: Detailed answer to the user's query
- `examples`: List of real-world examples illustrating the concept
- `related_nodes`: List of related nodes that might be of interest
- `suggested_questions`: List of follow-up questions to guide exploration

### Node Examples

The Node Chat feature includes enhancements to the existing `/node/{graph_id}/{node_id}` endpoint, which now returns examples in its response, providing practical applications of the concept.

### Usage Example

```python
import requests
import json

url = "http://localhost:5001/api/node-chat"
payload = {
    "node_id": "node_1",
    "graph_id": "67dbbafc3b11728551f5ce4c",
    "query": "How does this concept apply to healthcare organizations?",
    "document_id": "67dbac15ea53f25878bfa9fd"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

print(f"Response: {data['response']}")
print("\nExamples:")
for example in data['examples']:
    print(f"- {example['title']}: {example['description']}")

print("\nSuggested questions:")
for question in data['suggested_questions']:
    print(f"- {question}")
```

## Context Parameter Reference

The API supports various context parameters to tailor responses to specific organizational contexts:

### Company Attributes

- **size**: Company size
  - `small`: < 50 employees
  - `medium`: 50-500 employees
  - `large`: 500-5000 employees
  - `enterprise`: > 5000 employees

- **maturity**: Company maturity stage
  - `startup`: Early stage, establishing business model
  - `growth`: Rapid expansion phase
  - `mature`: Established company, stable operations
  - `declining`: Company facing declining market position

- **industry**: Industry sector (any string value)
  - Examples: `technology`, `healthcare`, `finance`, `manufacturing`, `retail`, `public_sector`

### Management Role

The role of the person asking the question:
- `founder`: Company founder/entrepreneur
- `c_level`: C-suite executive (CEO, COO, CTO, etc.)
- `middle_management`: Mid-level management
- `team_lead`: Team or department leader
- `consultant`: External consultant

### Challenge Type

The type of business challenge being faced:
- `growth`: Scaling and expansion challenges
- `efficiency`: Operational optimization
- `innovation`: New product/service development
- `organizational_restructuring`: Reorganization
- `digital_transformation`: Technology adoption/transition

### Environmental Factors

- **market_volatility**: Level of market volatility
  - `low`: Stable, predictable market
  - `medium`: Moderate changes and uncertainty
  - `high`: Rapidly changing, unpredictable market

- **competitive_pressure**: Level of competitive pressure
  - `low`: Few competitors, dominant position
  - `medium`: Average competitive landscape
  - `high`: Intense competition, crowded market

- **regulatory_environment**: Regulatory constraints
  - `relaxed`: Minimal regulatory requirements
  - `moderate`: Standard regulatory environment
  - `strict`: Heavily regulated industry/market

## Error Handling

The API uses standard HTTP status codes to indicate success or failure:

- `200 OK`: The request was successful
- `201 Created`: The resource was successfully created
- `400 Bad Request`: The request was malformed or invalid
- `404 Not Found`: The requested resource was not found
- `500 Internal Server Error`: An unexpected error occurred

Error responses include a JSON object with details:

```json
{
  "error": "Error type or message",
  "message": "Detailed error description"
}
```

## Implementation Notes

- The API processes queries asynchronously, so you must check the query status to determine when processing is complete
- Knowledge graphs are hierarchical with layers representing different levels of abstraction
- The context enrichment parameters significantly affect the content and structure of generated knowledge graphs 
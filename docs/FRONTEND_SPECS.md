# St. Gallen Management Model Frontend Specifications

## Overview

The frontend application will provide an intuitive interface for interacting with the St. Gallen Management Model API. Users will be able to submit queries about management concepts, visualize knowledge graphs, and explore connections between different management principles.

## Technology Stack

- **Framework**: React.js with TypeScript
- **State Management**: Redux or Context API
- **UI Components**: Material-UI or Tailwind CSS
- **Graph Visualization**: D3.js or react-force-graph
- **API Communication**: Axios or Fetch API
- **Authentication**: JWT-based (if required)

## Core Features

1. **Query Interface**
   - Text input for management-related queries
   - Context parameter selectors (company size, industry, management role, etc.)
   - Document selection dropdown for choosing specific textbooks

2. **Graph Visualization**
   - Interactive force-directed graph visualization
   - Node highlighting and selection
   - Zoom and pan capabilities
   - Layer filtering for hierarchical exploration
   - Connection visibility toggle

3. **Node Details Panel**
   - Detailed information about selected nodes
   - Related concepts and connections
   - Source citations from the textbook
   - Example applications and case studies

4. **Document Management**
   - List of available documents/textbooks
   - Document upload functionality (admin only)
   - Document metadata display

5. **User History**
   - List of previous queries
   - Ability to revisit and modify past queries
   - Saved/favorited graphs

6. **Node Chat Interface**
   - Contextual chat focused on selected nodes
   - Follow-up questions about specific concepts
   - Related examples and applications

## Layout Structure

### Main Layout

The application will follow a responsive layout with three main sections:

```
+-----------------------------------------------------------------------+
|                             HEADER                                    |
|  [Logo] [App Title]                         [User Profile] [Settings] |
+-----------------------------------------------------------------------+
|                                                                       |
|  +-------------------+  +---------------------+  +----------------+   |
|  |                   |  |                     |  |                |   |
|  |  QUERY PANEL      |  |  GRAPH DISPLAY      |  |  DETAILS PANEL |   |
|  |                   |  |                     |  |                |   |
|  |  [Query Input]    |  |                     |  |  [Node Title]  |   |
|  |                   |  |                     |  |                |   |
|  |  [Context Params] |  |  [Interactive       |  |  [Description] |   |
|  |                   |  |   Knowledge Graph]  |  |                |   |
|  |  [Submit Button]  |  |                     |  |  [Relevance]   |   |
|  |                   |  |                     |  |                |   |
|  |  [Document        |  |  [Layer Controls]   |  |  [Connections] |   |
|  |   Selection]      |  |                     |  |                |   |
|  |                   |  |  [Connection        |  |  [Examples]    |   |
|  |  [History List]   |  |   Controls]         |  |                |   |
|  |                   |  |                     |  |  [Chat with    |   |
|  |                   |  |                     |  |   Node Button] |   |
|  +-------------------+  +---------------------+  +----------------+   |
|                                                                       |
+-----------------------------------------------------------------------+
|                             FOOTER                                    |
|  [About] [Documentation] [API Status]                  [Version]      |
+-----------------------------------------------------------------------+
```

### Query Panel (Left Sidebar - 25% width)

- **Text Input**: Positioned at the top, full width of the panel, with placeholder text suggesting example queries
- **Context Parameters**: Collapsible accordion sections below the input:
  - Company section (size, maturity, industry dropdowns)
  - Role section (management level dropdown)
  - Environment section (market volatility, competition sliders)
  - Challenge type dropdown
- **Document Selection**: Dropdown menu to select specific textbooks
- **Submit Button**: Prominent button with loading state indicator
- **History List**: Collapsible section showing previous queries with timestamps

### Graph Display (Center - 50% width)

- **Knowledge Graph Visualization**: The main central area showing the interactive force-directed graph
- **Layer Controls**: Horizontal tabs or dropdown at the top to filter by layer (0, 1, 2)
- **Connection Toggle**: Switch to show/hide connections between nodes
- **Zoom Controls**: Bottom-right corner controls for zoom in/out and fit-to-view
- **Selection Controls**: Option to select multiple nodes for comparison
- **Graph Export**: Button to export the current graph as an image

### Details Panel (Right Sidebar - 25% width)

- **Node Information**: When a node is selected:
  - Title (top, larger font)
  - Description (summary of the concept)
  - Relevance score (visual indicator like a meter)
  - Connection list (with strength indicators)
  - Source citations (collapsible section with quotes)
  - Examples (real-world applications of the concept)
- **Chat Interface Button**: Button to expand the node chat functionality
- **Related Nodes**: Visual links to connected nodes for easy navigation

### Node Chat Interface (Expands from Details Panel)

```
+------------------------------------------------------+
|  CHAT WITH NODE: [Node Title]           [Close] [X]  |
+------------------------------------------------------+
|                                                      |
|  [Node context and description summary]              |
|                                                      |
|  [Chat history with AI responses about the node]     |
|                                                      |
|  User: How does this concept apply to healthcare?    |
|                                                      |
|  AI: In healthcare settings, this concept helps...   |
|                                                      |
|  +------------------------------------------------+  |
|  | Ask a question about this concept...    [Send] |  |
|  +------------------------------------------------+  |
|                                                      |
|  [Suggested questions about this node]              |
|                                                      |
+------------------------------------------------------+
```

### Responsive Design Considerations

- On tablet devices, the layout will adjust to:
  - Query panel collapses to a top bar with expandable sections
  - Graph display takes 60% of the width
  - Details panel takes 40% of the width

- On mobile devices:
  - Single column layout with collapsible sections
  - Query panel at top (collapsible)
  - Graph display in middle (expandable to full screen)
  - Details panel at bottom (collapsible)
  - Bottom navigation for switching between views

## Implementation Flow

### 1. Initial Setup and Authentication

1. Create project structure and install dependencies
2. Set up routing with React Router
3. Implement API service layer
4. Create authentication screens (if required)

### 2. Query Interface Implementation

1. Build the main query form component
   - Text input with autocomplete suggestions
   - Context parameter selectors with appropriate validation
   - Document selection dropdown populated from `/api/documents` endpoint
2. Implement query submission to `/api/query` endpoint
3. Add loading state feedback during graph generation
4. Handle error states and validation

### 3. Graph Visualization Implementation

1. Implement the graph visualization component
   - Set up D3.js or react-force-graph integration
   - Create node and link rendering functions
   - Implement interaction handlers (click, hover, zoom)
2. Connect to `/api/graph/{graph_id}` endpoint
3. Add layer filtering controls connected to `/api/graph/{graph_id}?layer={layer_num}`
4. Implement connections toggle using `/api/connections/{graph_id}` endpoint

### 4. Node Details Panel Implementation

1. Create the node details component
   - Display node title, description, and relevance score
   - Show related nodes and connections
   - Include source citations if available
   - Show examples and applications of the concept
2. Connect to `/api/node/{graph_id}/{node_id}` endpoint
3. Add navigation between related nodes

### 5. Document Management Implementation

1. Build document list component using `/api/documents` endpoint
2. Implement document upload form (admin only)
   - File selection with drag-and-drop
   - Metadata input fields
   - Progress indicators
3. Connect to `/api/document` endpoint for uploads

### 6. User History Implementation

1. Create query history component using `/api/user/{user_id}/queries` endpoint
2. Implement functionality to revisit past queries
3. Add saving/favoriting capability for important graphs

### 7. Node Chat Implementation

1. Design and implement the node chat interface
   - Create expandable chat panel component
   - Build message display and input components
   - Implement conversation history state management
2. Connect to new `/api/node-chat` endpoint (to be created)
3. Add suggested questions based on node content
4. Implement contextual awareness based on selected node(s)

### 8. Integration and Polish

1. Ensure consistent styling and responsive design
2. Implement proper error handling and user feedback
3. Add keyboard shortcuts and accessibility features
4. Optimize performance for large graphs

## API Integration

The frontend will communicate with the following key API endpoints:

| Endpoint | Purpose | Frontend Component |
|----------|---------|-------------------|
| `/api/query` | Submit new queries | Query Form |
| `/api/graph/{graph_id}` | Retrieve graph data | Graph Visualization |
| `/api/connections/{graph_id}` | Get graph connections | Graph Visualization |
| `/api/node/{graph_id}/{node_id}` | Get node details | Node Details Panel |
| `/api/documents` | List available documents | Document List |
| `/api/document` | Upload new documents | Document Upload Form |
| `/api/user/{user_id}/queries` | Get user's query history | History Component |
| `/api/node-chat` | Chat about specific nodes | Node Chat Interface |

## Innovative Interaction Features

### 1. Node Chat Interface

The Node Chat feature will enable users to have contextual conversations about specific nodes in the knowledge graph:

- **Functionality**:
  - Users can select a node and click "Chat with Node" to open a dedicated chat interface
  - The system uses the node's details as context for the conversation
  - Users can ask specific questions about the concept represented by the node
  - The AI responds with tailored explanations, examples, and applications

- **Implementation Requirements**:
  - Create a new backend endpoint `/api/node-chat` that accepts:
    - `node_id`: The ID of the selected node
    - `graph_id`: The ID of the current graph
    - `query`: The user's question about the node
    - `document_id`: The source document ID
    - `chat_history`: Previous messages in the conversation (optional)
  
  - The backend should:
    - Extract the node's details and connections
    - Use this as additional context for the RAG system
    - Generate a response that specifically addresses the question in relation to the node
    - Include examples and practical applications when appropriate

- **User Experience**:
  - Suggested questions based on node content
  - Ability to reference other nodes in questions
  - Option to save interesting insights from the chat
  - Visual indicators showing connections between chat responses and other nodes

### 2. Multi-Node Comparison

- Allow users to select multiple nodes for side-by-side comparison
- Display similarities, differences, and relationships between selected nodes
- Enable filtering the graph to show only the paths between selected nodes

### 3. Interactive Tutorials

- Guided tours of the St. Gallen Management Model concepts
- Step-by-step exploration of each layer and component
- Interactive exercises to test understanding of relationships

### 4. Collaborative Annotation

- Allow users to add personal notes to nodes and connections
- Enable sharing of annotated graphs with team members
- Support for collaborative graph exploration in real-time

### 5. Integration with Business Tools

- Export insights to common business tools (PowerPoint, Word, Notion, etc.)
- Create structured reports based on graph exploration
- Generate action plans based on model recommendations

## Real-World Example: Management Consulting Scenario

### Scenario

A management consultant is working with a mid-sized technology company facing organizational restructuring challenges. The consultant wants to use the St. Gallen Management Model to develop insights and recommendations.

### Implementation Example Flow

1. **Authentication**
   - The consultant logs into the application with their credentials.

2. **Query Submission**
   - The consultant navigates to the query interface.
   - They enter the query: "How can the St. Gallen Management Model help with organizational restructuring in a technology company?"
   - They set context parameters:
     - Company size: medium
     - Industry: technology
     - Management role: executive
     - Challenge type: organizational_restructuring
     - Market volatility: high
   - They select "St. Gallen Management Model" textbook (document ID: 67dbac15ea53f25878bfa9fd)
   - They submit the query.

3. **Graph Visualization**
   - The system generates a knowledge graph with the following main components:
     - **Environmental Spheres** (Layer 1)
       - Technological Environment (Layer 2)
       - Economic Environment (Layer 2)
     - **Stakeholders** (Layer 1)
       - Employees (Layer 2)
       - Management (Layer 2)
       - Customers (Layer 2)
     - **Resources** (Layer 1)
       - Human Capital (Layer 2)
       - Organizational Structure (Layer 2)
     - **Management Processes** (Layer 1)
       - Strategic Planning (Layer 2)
       - Operational Implementation (Layer 2)

4. **Exploring Node Details**
   - The consultant clicks on the "Organizational Structure" node.
   - The details panel shows:
     - Description: "The formal arrangement of roles, responsibilities, and relationships within an organization."
     - Relevance: 9/10
     - Connections to:
       - "Human Capital" (strong connection)
       - "Strategic Planning" (medium connection)
       - "Employees" (strong connection)
     - The panel also shows relevant quotes from the textbook about organizational structure.
     - Examples section shows: "Spotify's squad-based structure," "Google's pod organization," and "Holacracy implementation at Zappos"

5. **Node Chat Interaction**
   - The consultant clicks "Chat with Node" for the Organizational Structure node
   - They ask: "What are the key considerations when restructuring organizational processes in a high-tech company?"
   - The system responds with detailed insights specifically about organizational structure in technology companies, citing examples from the textbook
   - The consultant asks follow-up questions about change management during restructuring
   - The system provides tailored responses specific to this context

6. **Filtering and Exploration**
   - The consultant filters to show only Layer 1 nodes for a high-level overview.
   - They toggle connections to see relationships between main components.
   - They explore how "Management Processes" connects to other components.

7. **Saving and Sharing**
   - The consultant saves the graph to revisit later.
   - They export the visualization as an image to include in their presentation.
   - They make notes about key insights from the model.

8. **Iterative Refinement**
   - Based on initial insights, the consultant creates a new query: "What are the critical success factors for restructuring the organizational processes according to the St. Gallen Management Model?"
   - The system generates a new graph focused on this specific aspect.
   - The consultant compares both graphs to develop comprehensive recommendations.

## Frontend Mockups

Frontend developers should create wireframes and mockups for:

1. Main query interface with context parameters
2. Graph visualization with filtering controls
3. Node details panel with connections display
4. Document management interface
5. User history and saved graphs view
6. Node chat interface


## Conclusion

This frontend implementation will provide an intuitive interface for exploring the St. Gallen Management Model and generate valuable insights for management professionals. The application will leverage the powerful backend API to create interactive visualizations and deliver context-rich information about management concepts. The addition of the Node Chat feature significantly enhances the learning and exploration experience, allowing users to dive deeper into specific concepts and receive tailored guidance based on their unique contexts. 
import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, LLM_MODEL
from app.services.embeddings_service import EmbeddingsService

class RAGService:
    """Service to handle Retrieval Augmented Generation for management insights"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_service = EmbeddingsService()
        self.llm_model = LLM_MODEL
    
    def generate_context(self, query, context_params=None, max_chunks=8):
        """
        Generate context for LLM by retrieving relevant passages
        
        Args:
            query (str): User query
            context_params (dict): Optional context parameters
            max_chunks (int): Maximum number of chunks to retrieve
            
        Returns:
            str: Combined context from relevant passages
        """
        # Use context parameters to refine the search if provided
        if context_params:
            # Enhance query with context parameters
            context_query = f"{query} for "
            
            if 'company_size' in context_params:
                context_query += f"{context_params['company_size']} sized company "
            
            if 'maturity_stage' in context_params:
                context_query += f"in {context_params['maturity_stage']} stage "
            
            if 'industry' in context_params:
                context_query += f"in {context_params['industry']} industry "
            
            if 'management_challenge' in context_params:
                context_query += f"facing {context_params['management_challenge']} challenge "
            
            # Use the enhanced query for search
            chunks = self.embedding_service.search(context_query, limit=max_chunks)
        else:
            # Use the original query if no context parameters
            chunks = self.embedding_service.search(query, limit=max_chunks)
        
        if not chunks:
            return "No relevant information found."
        
        # Combine chunks into context
        context = "\n\n".join([f"PASSAGE {i+1}:\n{chunk['text']}" for i, chunk in enumerate(chunks)])
        
        return context
    
    def generate_layered_graph(self, query, context_params=None):
        """
        Generate a structured layered graph based on the user query and retrieved context
        
        Args:
            query (str): User query about management decision
            context_params (dict): Optional context parameters
            
        Returns:
            tuple: (graph_data, connections) where:
                - graph_data is the hierarchical graph structure
                - connections is a list of connections between nodes
        """
        try:
            # Get relevant context from vector DB
            context = self.generate_context(query, context_params)
            
            # Define the system prompt for layered graph generation
            system_prompt = """You are an expert in the St. Gallen Management Model, a comprehensive framework for business management.
            
            Your task is to create a layered knowledge graph in JSON format based on the user's query and relevant context from the St. Gallen Management Model.
            
            The knowledge graph should:
            1. Directly address the user's query
            2. Present information in a structured, hierarchical format
            3. Include only the most relevant information from the provided context
            4. Adapt the answer based on the provided context parameters such as:
               - Company attributes (size, maturity, industry)
               - Management role of the person asking the question
               - Type of business challenge they're facing
               - Environmental factors affecting the organization
            
            When context parameters are provided, tailor your response to be most relevant to that specific situation.
            For example:
            - For small companies, emphasize lean processes and resource efficiency
            - For C-level roles, focus on strategic and normative dimensions
            - For growth challenges, highlight scaling strategies and organizational development
            - For volatile environments, emphasize adaptability and resilience
            
            The output should be a valid JSON object with the following structure:
            {
              "id": "node_0",
              "title": "Central Topic/Decision",
              "description": "Clear, concise explanation of the central topic or answer to the query",
              "layer": 0,
              "relevance": 10,
              "children": [
                {
                  "id": "node_1",
                  "title": "Core Element 1",
                  "description": "Description of this element",
                  "layer": 1,
                  "relevance": 9,
                  "children": [...]
                },
                ...
              ]
            }
            
            Where:
            - "id": Unique identifier for each node (e.g., "node_0", "node_1")
            - "title": Concise title for the node (max 5 words)
            - "description": Detailed explanation (1-2 sentences)
            - "layer": Integer representing hierarchical depth (0-4)
            - "relevance": Integer (1-10) representing importance to query
            - "children": Array of child nodes (with the same structure)
            
            Make the graph comprehensive but focused on the query topic."""
            
            # Create the user prompt with query, context, and context parameters
            user_prompt = f"""
            QUERY: {query}
            
            RELEVANT CONTEXT FROM ST. GALLEN MANAGEMENT MODEL:
            {context}
            """
            
            # Add context parameters if provided
            if context_params:
                user_prompt += "\n\nCONTEXT PARAMETERS:\n"
                
                # Process document_id separately
                if 'document_id' in context_params:
                    user_prompt += f"- document_id: {context_params['document_id']}\n"
                
                # Process company attributes if present
                if 'company' in context_params:
                    company = context_params['company']
                    user_prompt += "- Company Attributes:\n"
                    for attr, value in company.items():
                        user_prompt += f"  * {attr}: {value}\n"
                
                # Process management role
                if 'management_role' in context_params:
                    user_prompt += f"- Management Role: {context_params['management_role']}\n"
                
                # Process challenge type
                if 'challenge_type' in context_params:
                    user_prompt += f"- Challenge Type: {context_params['challenge_type']}\n"
                
                # Process environmental factors
                if 'environment' in context_params:
                    env = context_params['environment']
                    user_prompt += "- Environmental Factors:\n"
                    for factor, value in env.items():
                        user_prompt += f"  * {factor}: {value}\n"
                
                # Process any other parameters
                for key, value in context_params.items():
                    if key not in ['document_id', 'company', 'management_role', 'challenge_type', 'environment']:
                        user_prompt += f"- {key}: {value}\n"
            
            user_prompt += """
            Based on the query and the provided context from the St. Gallen Management Model, create a structured layered JSON graph as specified.
            
            The graph should represent the St. Gallen Management Model with layers:
            - Layer 0: Central topic/decision
            - Layer 1: Core SGMM elements (Environment, Organization, Management)
            - Layer 2: Main management dimensions
            - Layer 3: Specific concepts and methodologies
            - Layer 4: Practical applications (if relevant)
            
            Also generate the list of non-hierarchical connections between related nodes.
            
            Ensure all JSON is properly structured with the required fields.
            """
            
            # Generate the response
            completion = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            # Extract and parse the JSON response
            result = completion.choices[0].message.content
            
            # Find JSON in the response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                response_data = json.loads(json_str)
                
                # Extract graph and connections
                if "graph" in response_data and "connections" in response_data:
                    return response_data["graph"], response_data["connections"]
                elif "graph" in response_data:
                    return response_data["graph"], []
                else:
                    return response_data, []  # Assume the whole response is the graph if not properly structured
            else:
                # If no valid JSON was found, generate a simpler response
                return self._generate_fallback_graph(query), []
                
        except Exception as e:
            print(f"Error generating layered graph: {str(e)}")
            return self._generate_fallback_graph(query), []
    
    def generate_graph(self, query, context_params=None):
        """
        Generate a structured graph based on the user query and retrieved context
        Legacy method for backward compatibility
        
        Args:
            query (str): User query about management decision
            context_params (dict): Optional context parameters
            
        Returns:
            dict: JSON structure representing the management decision graph
        """
        # Call the new layered graph method and return only the graph part
        graph_data, _ = self.generate_layered_graph(query, context_params)
        return graph_data
    
    def _generate_fallback_graph(self, query):
        """Generate a simple fallback graph if the main generation fails"""
        return {
            "id": "root",
            "title": query,
            "description": "Decision analysis based on the St. Gallen Management Model",
            "layer": 0,
            "relevance": 10,
            "children": [
                {
                    "id": "env_analysis",
                    "title": "Environmental & Stakeholder Analysis",
                    "description": "Analysis of external factors and stakeholders",
                    "layer": 1,
                    "relevance": 8,
                    "children": [
                        {
                            "id": "external_factors",
                            "title": "External Factors",
                            "description": "Consider technological, economic, and social influences",
                            "layer": 2,
                            "relevance": 7,
                            "children": []
                        },
                        {
                            "id": "stakeholders",
                            "title": "Stakeholder Mapping",
                            "description": "Identify and analyze key stakeholders",
                            "layer": 2,
                            "relevance": 7,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "strategy",
                    "title": "Strategy & Business Model",
                    "description": "Strategic considerations and business model design",
                    "layer": 1,
                    "relevance": 9,
                    "children": [
                        {
                            "id": "value_prop",
                            "title": "Value Proposition",
                            "description": "Define the unique value offering",
                            "layer": 2,
                            "relevance": 8,
                            "children": []
                        },
                        {
                            "id": "comp_advantage",
                            "title": "Competitive Advantage",
                            "description": "Identify sustainable competitive advantages",
                            "layer": 2,
                            "relevance": 8,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "organization",
                    "title": "Organizational Structure & Processes",
                    "description": "Internal organizational considerations",
                    "layer": 1,
                    "relevance": 7,
                    "children": [
                        {
                            "id": "structure",
                            "title": "Organizational Structure",
                            "description": "Design appropriate organizational structures",
                            "layer": 2,
                            "relevance": 6,
                            "children": []
                        },
                        {
                            "id": "processes",
                            "title": "Management Processes",
                            "description": "Establish effective management processes",
                            "layer": 2,
                            "relevance": 6,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "implementation",
                    "title": "Implementation & Development",
                    "description": "Approaches to implementation and change management",
                    "layer": 1,
                    "relevance": 8,
                    "children": [
                        {
                            "id": "change_mgmt",
                            "title": "Change Management",
                            "description": "Manage organizational change effectively",
                            "layer": 2,
                            "relevance": 7,
                            "children": []
                        },
                        {
                            "id": "implementation",
                            "title": "Implementation Approach",
                            "description": "Plan the implementation strategy",
                            "layer": 2,
                            "relevance": 7,
                            "children": []
                        }
                    ]
                }
            ]
        } 
import json
from app.services.rag_service import RAGService
from app.models.db_models import Query, Graph
from app.config import LLM_MODEL
from openai import OpenAI
import re

class GraphService:
    """Service to handle decision graph generation and management"""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.openai_client = OpenAI()
        self.llm_model = LLM_MODEL
    
    def generate_graph_for_query(self, user_id, query_text, context_params=None):
        """
        Generate a decision graph for a user query
        
        Args:
            user_id (str): ID of the user making the query
            query_text (str): The query text
            context_params (dict): Optional context parameters
            
        Returns:
            tuple: (query_id, graph_id) if successful, (query_id, None) if failed
        """
        try:
            # Create query record
            query_id = Query.create(user_id, query_text, context_params)
            
            # Generate graph data and connections
            graph_data, connections = self.rag_service.generate_layered_graph(query_text, context_params)
            
            if not graph_data:
                Query.update_status(query_id, "failed")
                return query_id, None
            
            # Store graph in database
            graph_id = Graph.create(query_id, graph_data)
            
            # Store connections if any
            if connections and len(connections) > 0:
                Graph.add_connections(graph_id, connections)
            
            # Update query status
            Query.update_status(query_id, "completed", graph_id)
            
            return query_id, graph_id
            
        except Exception as e:
            print(f"Error generating graph for query: {str(e)}")
            if locals().get('query_id'):
                Query.update_status(query_id, "failed")
            return locals().get('query_id'), None
    
    def get_graph(self, graph_id):
        """
        Get a graph by ID
        
        Args:
            graph_id (str): ID of the graph
            
        Returns:
            dict: Graph data
        """
        try:
            graph = Graph.get_by_id(graph_id)
            if not graph:
                return None
                
            return graph["graph_data"]
            
        except Exception as e:
            print(f"Error retrieving graph: {str(e)}")
            return None
    
    def get_graph_with_connections(self, graph_id):
        """
        Get a graph with its connections by ID
        
        Args:
            graph_id (str): ID of the graph
            
        Returns:
            dict: Graph data with connections
        """
        try:
            graph = Graph.get_by_id(graph_id)
            if not graph:
                return None
                
            connections = Graph.get_connections(graph_id)
            
            return {
                "graph": graph["graph_data"],
                "connections": connections
            }
            
        except Exception as e:
            print(f"Error retrieving graph with connections: {str(e)}")
            return None
    
    def get_graph_for_query(self, query_id):
        """
        Get graph data for a query
        
        Args:
            query_id (str): ID of the query
            
        Returns:
            dict: Graph data
        """
        try:
            graph = Graph.get_by_query_id(query_id)
            if not graph:
                return None
                
            return graph["graph_data"]
            
        except Exception as e:
            print(f"Error retrieving graph for query: {str(e)}")
            return None
    
    def get_graph_by_layer(self, graph_id, layer=None):
        """
        Get graph data filtered by layer
        
        Args:
            graph_id (str): ID of the graph
            layer (int, optional): Layer to filter by
            
        Returns:
            dict: Filtered graph data
        """
        try:
            graph_data = self.get_graph(graph_id)
            if not graph_data:
                return None
                
            if layer is None:
                return graph_data
                
            # Filter nodes by layer
            return self._filter_graph_by_layer(graph_data, layer)
            
        except Exception as e:
            print(f"Error retrieving graph by layer: {str(e)}")
            return None
    
    def _filter_graph_by_layer(self, node, target_layer):
        """
        Helper method to filter a graph by layer
        
        Args:
            node (dict): Current node to process
            target_layer (int): Target layer to keep
            
        Returns:
            dict: Filtered node and its children
        """
        # Create a copy of the node to avoid modifying the original
        filtered_node = node.copy()
        
        # Check if this node is at or below the target layer
        current_layer = node.get("layer", 0)
        
        if current_layer > target_layer:
            # Skip this node as it's beyond the target layer
            return None
            
        # Process children
        if "children" in node and node["children"]:
            filtered_children = []
            
            for child in node["children"]:
                filtered_child = self._filter_graph_by_layer(child, target_layer)
                if filtered_child:
                    filtered_children.append(filtered_child)
                    
            filtered_node["children"] = filtered_children
        
        return filtered_node
    
    def get_filtered_graph(self, graph_id, context_params):
        """
        Get graph filtered by relevance based on context parameters
        
        Args:
            graph_id (str): ID of the graph
            context_params (dict): Context parameters for filtering
            
        Returns:
            dict: Filtered graph based on relevance
        """
        try:
            graph_data = self.get_graph(graph_id)
            if not graph_data:
                return None
                
            # Apply relevance filtering based on context parameters
            # This is a simplified implementation
            min_relevance = 5  # Default minimum relevance threshold
            
            if context_params and "min_relevance" in context_params:
                min_relevance = int(context_params["min_relevance"])
                
            return self._filter_graph_by_relevance(graph_data, min_relevance)
            
        except Exception as e:
            print(f"Error filtering graph by relevance: {str(e)}")
            return None
    
    def _filter_graph_by_relevance(self, node, min_relevance):
        """
        Helper method to filter a graph by minimum relevance score
        
        Args:
            node (dict): Current node to process
            min_relevance (int): Minimum relevance score to include
            
        Returns:
            dict: Filtered node and its children
        """
        # Create a copy of the node to avoid modifying the original
        filtered_node = node.copy()
        
        # Check if this node meets the relevance threshold
        relevance = node.get("relevance", 0)
        
        if relevance < min_relevance:
            # Skip this node as it doesn't meet the relevance threshold
            return None
            
        # Process children
        if "children" in node and node["children"]:
            filtered_children = []
            
            for child in node["children"]:
                filtered_child = self._filter_graph_by_relevance(child, min_relevance)
                if filtered_child:
                    filtered_children.append(filtered_child)
                    
            filtered_node["children"] = filtered_children
        
        return filtered_node
    
    def update_graph(self, graph_id, graph_data):
        """
        Update graph data
        
        Args:
            graph_id (str): ID of the graph
            graph_data (dict): New graph data
            
        Returns:
            bool: Success status
        """
        try:
            Graph.update(graph_id, graph_data)
            return True
            
        except Exception as e:
            print(f"Error updating graph: {str(e)}")
            return False
    
    def extract_node_details(self, graph_data, node_id):
        """
        Extract details for a specific node in the graph
        
        Args:
            graph_data (dict): Graph data
            node_id (str): ID of the node to extract
            
        Returns:
            dict: Node details with path information and examples
        """
        try:
            # Start with the root node
            if graph_data["id"] == node_id:
                node_info = {
                    "node": graph_data,
                    "path": [graph_data],
                    "level": 0
                }
                
                # Generate examples for this node
                node_info["examples"] = self.generate_examples_for_node(graph_data)
                return node_info
                
            # Recursive helper function
            def find_node(current_node, path, level):
                # Check if current node is the target
                if current_node["id"] == node_id:
                    node_info = {
                        "node": current_node,
                        "path": path + [current_node],
                        "level": level
                    }
                    
                    # Generate examples for this node
                    node_info["examples"] = self.generate_examples_for_node(current_node)
                    return node_info
                
                # Check children if they exist
                if "children" in current_node and current_node["children"]:
                    for child in current_node["children"]:
                        result = find_node(child, path + [current_node], level + 1)
                        if result:
                            return result
                
                return None
            
            # Start search from root
            return find_node(graph_data, [], 0)
            
        except Exception as e:
            print(f"Error extracting node details: {str(e)}")
            return None
    
    def generate_examples_for_node(self, node):
        """
        Generate examples for a specific node
        
        Args:
            node (dict): Node data
            
        Returns:
            list: Examples for this node
        """
        try:
            # Check if we already have examples stored in the node
            if "examples" in node and node["examples"]:
                return node["examples"]
            
            # Generate examples using LLM
            title = node.get("title", "")
            description = node.get("description", "")
            
            # Create prompt for examples generation
            prompt = f"""Generate 2-3 real-world examples that illustrate the following management concept from the St. Gallen Management Model:
            
            Concept: {title}
            Description: {description}
            
            Each example should:
            1. Have a clear title (e.g., company name or scenario)
            2. Briefly explain how the concept is applied in that context
            3. Be realistic and preferably based on actual cases
            
            Format each example as:
            Example: [Title]
            [Description of the application...]
            """
            
            # Generate examples
            try:
                completion = self.openai_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                
                response_text = completion.choices[0].message.content
                return self._extract_examples(response_text)
                
            except Exception as e:
                print(f"Error generating examples with LLM: {str(e)}")
                # Return default examples if LLM generation fails
                return self._generate_default_examples(title)
                
        except Exception as e:
            print(f"Error generating examples for node: {str(e)}")
            return []
    
    def _extract_examples(self, text):
        """Extract examples from text using regex"""
        examples = []
        
        # Pattern to match examples
        pattern = r"Example:?\s*(.+?)[\n\r]+([\s\S]+?)(?=Example|$)"
        matches = re.finditer(pattern, text, re.MULTILINE)
        
        for match in matches:
            title = match.group(1).strip()
            description = match.group(2).strip()
            
            # Check if the title contains a colon (common format)
            if ":" in title and not title.startswith("Example:"):
                parts = title.split(":", 1)
                title = parts[0].strip()
                # Prepend the rest to the description
                description = f"{parts[1].strip()} {description}"
            
            examples.append({
                "title": title,
                "description": description
            })
        
        # If no examples found with the pattern, try a simpler approach
        if not examples:
            # Look for paragraphs that seem like examples
            paragraphs = text.split("\n\n")
            for para in paragraphs:
                if "example" in para.lower() or "case" in para.lower() or "instance" in para.lower():
                    # Try to extract a title from the first sentence
                    sentences = para.split(". ", 1)
                    if len(sentences) > 1:
                        title = sentences[0].strip()
                        description = sentences[1].strip()
                    else:
                        title = "Example"
                        description = para.strip()
                    
                    examples.append({
                        "title": title,
                        "description": description
                    })
        
        return examples
    
    def _generate_default_examples(self, concept_title):
        """Generate default examples if LLM generation fails"""
        return [
            {
                "title": "Generic Application",
                "description": f"Organizations typically apply {concept_title} by integrating it into their strategic planning process to ensure alignment with business objectives."
            },
            {
                "title": "Implementation Example",
                "description": f"A medium-sized technology company implemented {concept_title} to improve their management structure and decision-making processes."
            }
        ]
    
    def get_node_connections(self, graph_id, node_id):
        """
        Get connections for a specific node
        
        Args:
            graph_id (str): ID of the graph
            node_id (str): ID of the node
            
        Returns:
            list: Connections for this node
        """
        try:
            return Graph.get_node_connections(graph_id, node_id)
        except Exception as e:
            print(f"Error getting node connections: {str(e)}")
            return [] 
import json
import re
from openai import OpenAI
from app.config import OPENAI_API_KEY, LLM_MODEL
from app.services.graph_service import GraphService
from app.services.embeddings_service import EmbeddingsService
from app.models.db_models import Document, Query

class NodeChatService:
    """Service to handle node-specific chat functionality"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.graph_service = GraphService()
        self.embeddings_service = EmbeddingsService()
        self.llm_model = LLM_MODEL
    
    def generate_chat_response(self, graph_id, node_id, query, document_id, chat_history=None, query_id=None):
        """
        Generate a chat response for a specific node
        
        Args:
            graph_id (str): ID of the graph
            node_id (str): ID of the node to chat about
            query (str): User query about the node
            document_id (str): ID of the document to use for context
            chat_history (list, optional): Previous chat messages
            query_id (str, optional): ID of the original query that created the graph
            
        Returns:
            dict: Response with text, examples, related nodes, and suggested questions
        """
        try:
            # Get graph and node details
            graph = self.graph_service.get_graph(graph_id)
            if not graph:
                return {"error": "Graph not found"}, 404
                
            node_details = self.graph_service.extract_node_details(graph, node_id)
            if not node_details:
                return {"error": "Node not found"}, 404
            
            # Get node data and metadata
            node = node_details["node"]
            node_title = node["title"]
            node_description = node["description"]
            node_layer = node["layer"]
            node_relevance = node["relevance"]
            
            # Get original query context if query_id is provided
            original_query_context = ""
            if query_id:
                original_query = Query.get_by_id(query_id)
                if original_query:
                    original_query_context = f"\nOriginal Query: {original_query.get('query_text', '')}\n"
            
            # Get node connections for additional context
            connections = self.graph_service.get_node_connections(graph_id, node_id)
            
            # Build node context string
            node_context = f"Node Title: {node_title}\nNode Description: {node_description}\n"
            node_context += f"Layer: {node_layer}\nRelevance: {node_relevance}/10\n"
            node_context += original_query_context
            
            # Add path information if available
            if "path" in node_details:
                path = node_details["path"]
                if path:
                    node_context += "\nNode Path (Hierarchical Position):\n"
                    for i, path_node in enumerate(path):
                        indent = "  " * i
                        node_context += f"{indent}- {path_node['title']}\n"
            
            # Add connections information
            if connections:
                node_context += "\nConnections to Other Nodes:\n"
                for conn in connections:
                    node_context += f"- Connected to '{conn['target_title']}': {conn.get('relationship_type', 'related')}\n"
            
            # Build chat history context
            chat_context = ""
            if chat_history and len(chat_history) > 0:
                chat_context = "Previous Conversation:\n"
                for msg in chat_history:
                    role = msg["role"].capitalize()
                    content = msg["content"]
                    chat_context += f"{role}: {content}\n"
            
            # Retrieve relevant document chunks
            document_context = self._retrieve_document_context(query, document_id, node_title, node_description)
            
            # Generate RAG response
            response_text = self._generate_rag_response(query, node_context, chat_context, document_context)
            
            # Extract examples from response
            examples = self._extract_examples(response_text)
            
            # Find related nodes
            related_nodes = self._find_related_nodes(graph, node_id, query)
            
            # Generate suggested questions
            suggested_questions = self._generate_suggested_questions(node_title, node_description, query, response_text)
            
            return {
                "success": True,
                "response": response_text,
                "examples": examples,
                "related_nodes": related_nodes,
                "suggested_questions": suggested_questions
            }
            
        except Exception as e:
            print(f"Error generating node chat response: {str(e)}")
            return {"error": f"Failed to generate response: {str(e)}"}, 500
    
    def _retrieve_document_context(self, query, document_id, node_title, node_description):
        """Retrieve relevant document chunks for the query and node"""
        try:
            # Enhance the search query with node information
            enhanced_query = f"{query} {node_title} {node_description}"
            
            # Get document details
            document = Document.get_by_id(document_id)
            if not document:
                print(f"Document not found: {document_id}")
                return ""
            
            # Use the embeddings service to search for relevant content
            chunks = self.embeddings_service.search(enhanced_query, limit=5)
            if not chunks:
                return "No relevant information found in the document."
            
            # Format the chunks
            formatted_chunks = ""
            for i, chunk in enumerate(chunks):
                formatted_chunks += f"PASSAGE {i+1}:\n{chunk['text']}\n\n"
            
            return formatted_chunks
            
        except Exception as e:
            print(f"Error retrieving document context: {str(e)}")
            return "Error retrieving relevant information from the document."
    
    def _generate_rag_response(self, query, node_context, chat_context, document_context):
        """Generate a RAG response using the LLM"""
        try:
            # Create system prompt
            system_prompt = """You are an expert in the St. Gallen Management Model, a comprehensive framework for business management.
            
            Your task is to answer questions about specific concepts within the model. For each question:
            1. Provide a clear, concise response directly addressing the query
            2. Explain the concept's role within the St. Gallen Management Model
            3. Include 2-3 real-world examples that illustrate the concept's application
            4. Mention any related concepts or connections that might be helpful
            
            Format your examples as follows:
            Example: [Title]
            [Description of the example and how it relates to the concept]
            
            Keep your explanations concise but informative, avoiding unnecessary technical jargon while maintaining accuracy."""
            
            # Create user prompt with all context
            user_prompt = f"""Question: {query}
            
            Information about this concept:
            {node_context}
            
            {chat_context}
            
            Relevant information from the St. Gallen Management Model:
            {document_context}
            
            Please provide a clear, helpful response with examples and practical applications.
            """
            
            # Generate response
            completion = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating RAG response: {str(e)}")
            return "I'm sorry, I encountered an error while generating a response."
    
    def _extract_examples(self, text):
        """Extract examples from the response text"""
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
    
    def _find_related_nodes(self, graph, node_id, query):
        """Find related nodes based on connections and semantic similarity"""
        related_nodes = []
        
        # Helper function to recursively search the graph
        def search_graph(node, level=0, found=False):
            # Skip the node itself
            if node['id'] == node_id:
                found = True
                return
            
            # If we found the target node, add siblings and parent's siblings as related
            if found and level > 0:
                # Add this node as related
                relevance = self._calculate_relevance(node['title'], node['description'], query)
                related_nodes.append({
                    "id": node['id'],
                    "title": node['title'],
                    "relevance": relevance
                })
            
            # Process children
            if 'children' in node and node['children']:
                for child in node['children']:
                    search_graph(child, level+1, found)
        
        # Start search from root
        search_graph(graph, 0, False)
        
        # Sort by relevance and limit to top 3
        related_nodes.sort(key=lambda x: x['relevance'], reverse=True)
        return related_nodes[:3]
    
    def _calculate_relevance(self, title, description, query):
        """Calculate relevance score between node and query"""
        # Simple relevance calculation based on term overlap
        # In a production system, this would use embeddings for better semantic matching
        query_terms = set(query.lower().split())
        node_terms = set((title + " " + description).lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(query_terms.intersection(node_terms))
        union = len(query_terms.union(node_terms))
        
        if union == 0:
            return 0.5  # Default value
        
        return round(intersection / union, 2)
    
    def _generate_suggested_questions(self, node_title, node_description, query, response):
        """Generate suggested follow-up questions"""
        # For now, provide default questions as a reliable solution
        # These questions are tailored to the node and will be helpful for most concepts
        return [
            f"How can {node_title} be measured or evaluated in practice?",
            f"What are the key challenges in managing {node_title} effectively?",
            f"How does {node_title} interact with other elements of the St. Gallen Management Model?"
        ] 
"""
Service for generating quiz questions about specific nodes in the knowledge graph.
"""
import json
import logging
from typing import Dict, List, Any, Optional

from app.models.db_models import Document, Graph, Query
from app.services.graph_service import GraphService
from app.services.llm_service import LLMService

class NodeQuizService:
    """
    Service for generating quiz questions to test user's understanding of knowledge graph nodes.
    """
    
    def __init__(self) -> None:
        """Initialize the NodeQuizService."""
        self.graph_service = GraphService()
        self.llm_service = LLMService()
        self.logger = logging.getLogger(__name__)
    
    def generate_quiz(self, graph_id: str, node_id: str, document_id: str, 
                      query_id: Optional[str] = None, num_questions: int = 5) -> Dict[str, Any]:
        """
        Generate quiz questions about a specific node in the graph.
        
        Args:
            graph_id: ID of the graph containing the node
            node_id: ID of the node to quiz about
            document_id: ID of the source document
            query_id: Optional ID of the original query that created the graph
            num_questions: Number of questions to generate (default: 5)
            
        Returns:
            Dict containing quiz questions, options, and correct answers
        """
        try:
            # Get graph
            graph = Graph.get_by_id(graph_id)
            if not graph:
                self.logger.error(f"Graph not found: {graph_id}")
                return {"error": "Graph not found"}
            
            # Get node details and establish context
            node_data = self.graph_service.extract_node_details(graph.get('graph_data', {}), node_id)
            if not node_data:
                self.logger.error(f"Node not found: {node_id} in graph {graph_id}")
                return {"error": "Node not found"}
            
            # Get document
            document = Document.get_by_id(document_id)
            if not document:
                self.logger.error(f"Document not found: {document_id}")
                return {"error": "Document not found"}
            
            # Get original query if query_id is provided
            original_query_text = None
            if query_id:
                query = Query.get_by_id(query_id)
                if query and 'query_text' in query:
                    original_query_text = query['query_text']
            
            # Get connected nodes for broader context
            connected_nodes = []
            connections = self.graph_service.get_node_connections(graph_id, node_id)
            if connections:
                for conn in connections:
                    connected_node_id = conn['source'] if conn['target'] == node_id else conn['target']
                    connected_node_data = self.graph_service.extract_node_details(graph.get('graph_data', {}), connected_node_id)
                    if connected_node_data:
                        connected_nodes.append(connected_node_data)
            
            # Create quiz context
            context = self._build_quiz_context(node_data, document, graph, connected_nodes, original_query_text)
            
            # Generate quiz questions
            return self._generate_questions(context, num_questions)
        
        except Exception as e:
            self.logger.error(f"Error generating quiz: {str(e)}")
            return {"error": f"Failed to generate quiz: {str(e)}"}
    
    def _build_quiz_context(self, node: Dict[str, Any], document: Dict[str, Any], graph: Dict[str, Any], 
                           connected_nodes: List[Dict[str, Any]], original_query_text: Optional[str]) -> str:
        """
        Build context for quiz generation.
        
        Args:
            node: The node data to generate questions about
            document: The source document
            graph: The graph containing the node
            connected_nodes: List of connected nodes
            original_query_text: The original query text
            
        Returns:
            String containing the context for quiz generation
        """
        context = f"Topic: {node.get('label', 'Unknown Topic')}\n\n"
        context += f"Description: {node.get('description', 'No description available')}\n\n"
        
        # Add examples if available
        if 'examples' in node and node['examples']:
            context += "Examples:\n"
            for example in node['examples']:
                context += f"- {example}\n"
            context += "\n"
        
        # Add related nodes
        if connected_nodes:
            context += "Related concepts:\n"
            for related_node in connected_nodes:
                # Limit description length if it's too long
                description = related_node.get('description', '')
                short_desc = description[:100] + '...' if len(description) > 100 else description
                context += f"- {related_node.get('label', 'Unknown')}: {short_desc}\n"
            context += "\n"
        
        # Add original query if available
        if original_query_text:
            context += f"Original query: {original_query_text}\n\n"
        
        # Add document information
        context += f"Source: {document.get('title', 'Unknown')} by {document.get('author', 'Unknown')}\n"
        
        return context
    
    def _generate_questions(self, context: str, num_questions: int = 5) -> Dict[str, Any]:
        """
        Generate multiple-choice quiz questions based on the provided context.
        
        Args:
            context: The context to base questions on
            num_questions: Number of questions to generate
            
        Returns:
            Dict containing quiz questions, options, and correct answers
        """
        prompt = f"""
        Based on the following information about a concept from the St. Gallen Management Model, create {num_questions} multiple-choice quiz questions to test understanding.

        {context}

        For each question:
        1. Create a question that tests understanding (not just memorization)
        2. Provide 4 options (A, B, C, D)
        3. Indicate the correct answer
        4. Add a brief explanation for why the answer is correct

        Ensure questions vary in difficulty and cover different aspects of the concept.
        Format your response as a JSON object with the following structure:
        {{
            "questions": [
                {{
                    "question": "Question text...",
                    "options": {{
                        "A": "First option",
                        "B": "Second option",
                        "C": "Third option",
                        "D": "Fourth option"
                    }},
                    "correct_answer": "A",
                    "explanation": "Explanation of why this answer is correct..."
                }},
                // More questions...
            ]
        }}
        """
        
        try:
            response = self.llm_service.generate_text(prompt)
            # Extract JSON from the response
            quiz_data = self._extract_json(response)
            
            # Validate quiz structure
            if not quiz_data or "questions" not in quiz_data:
                self.logger.error(f"Invalid quiz format: {response}")
                # Create a fallback quiz structure
                return self._create_fallback_quiz(context, num_questions)
            
            return quiz_data
        
        except Exception as e:
            self.logger.error(f"Error generating quiz questions: {str(e)}")
            return self._create_fallback_quiz(context, num_questions)
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from a text response.
        
        Args:
            text: Text potentially containing JSON
            
        Returns:
            Extracted JSON as Dict, or empty Dict if extraction fails
        """
        try:
            # Find JSON delimiters
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            return {}
        except json.JSONDecodeError:
            self.logger.error("JSON decode error extracting quiz data")
            return {}
    
    def _create_fallback_quiz(self, context: str, num_questions: int) -> Dict[str, Any]:
        """
        Create a fallback quiz when generation fails.
        
        Args:
            context: The context to base the fallback quiz on
            num_questions: Number of questions to generate
            
        Returns:
            Dict containing a simplified fallback quiz
        """
        self.logger.warning("Using fallback quiz generation")
        
        # Create a simpler prompt for a second attempt
        simpler_prompt = f"""
        Create {num_questions} basic multiple-choice questions about this topic:
        {context}
        
        Return only a JSON object with this structure:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
                    "correct_answer": "A",
                    "explanation": "Why A is correct"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_service.generate_text(simpler_prompt)
            quiz_data = self._extract_json(response)
            
            if quiz_data and "questions" in quiz_data:
                return quiz_data
            
            # If still failing, return a template structure
            return {
                "questions": [
                    {
                        "question": f"What is the main concept described in this node?",
                        "options": {
                            "A": "Option A",
                            "B": "Option B",
                            "C": "Option C",
                            "D": "Option D"
                        },
                        "correct_answer": "A",
                        "explanation": "This is a placeholder question. The quiz generation failed."
                    }
                ],
                "error": "Failed to generate custom quiz questions. Using placeholder."
            }
        except Exception as e:
            self.logger.error(f"Fallback quiz creation also failed: {str(e)}")
            return {"error": "Quiz generation failed completely"}
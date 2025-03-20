import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.db_models import Document, Context
from app.services.embeddings_service import EmbeddingsService

def create_sample_document():
    """Create a sample St. Gallen Management Model document in the database"""
    
    print("Creating sample document...")
    
    # Sample content from the St. Gallen Management Model textbook
    title = "St. Gallen Management Model - Core Concepts"
    content = """
    # St. Gallen Management Model: A Comprehensive Framework for Management
    
    ## Introduction to the St. Gallen Management Model
    
    The St. Gallen Management Model (SGMM) is a systematic framework for the description and design of management systems. Developed at the University of St. Gallen in Switzerland, it provides a holistic approach to understanding and managing organizations. The model considers business activities from an integrated perspective, examining the interrelationships between different elements of management.
    
    ## Environmental Spheres
    
    The SGMM recognizes three environmental spheres that influence organizational decisions:
    
    1. **Social Environment**: This includes societal values, norms, and cultural factors that shape organizational behavior and stakeholder expectations.
    
    2. **Technological Environment**: This encompasses technological trends, innovations, and infrastructure that can enable or constrain organizational capabilities.
    
    3. **Economic Environment**: This covers market conditions, economic policies, and industry structures that affect organizational performance and competition.
    
    Organizations must continuously monitor and adapt to changes in these environmental spheres to remain viable and successful.
    
    ## Stakeholder Perspectives
    
    The SGMM emphasizes the importance of managing relationships with various stakeholders, including:
    
    - Customers and users
    - Investors and shareholders
    - Employees and management
    - Suppliers and business partners
    - Government and regulatory bodies
    - Local communities and society at large
    
    Effective stakeholder management requires understanding the diverse needs, interests, and expectations of these groups and balancing them in a way that creates sustainable value.
    
    ## Strategy Development and Business Model Design
    
    The SGMM provides a framework for developing strategies and designing business models that are aligned with environmental conditions and stakeholder expectations. Key aspects include:
    
    - Analyzing environmental forces and stakeholder relationships
    - Defining the organization's purpose, vision, and mission
    - Formulating strategic goals and objectives
    - Designing business models that create, deliver, and capture value
    - Aligning resources and capabilities with strategic priorities
    
    The model emphasizes the importance of coherence and integration between different elements of strategy and business model design.
    
    ## Organizational Structure and Processes
    
    The SGMM addresses the design of organizational structures and processes that enable effective implementation of strategies and business models. This includes:
    
    - Defining organizational architecture and reporting relationships
    - Establishing governance mechanisms and decision-making processes
    - Designing core business processes and work flows
    - Implementing management systems for planning, control, and coordination
    - Creating communication channels and information flows
    
    The model emphasizes the need for structures and processes that are flexible, adaptive, and responsive to changing conditions.
    
    ## Implementation and Development Modes
    
    The SGMM recognizes different modes of implementation and organizational development, including:
    
    - Optimization and incremental improvement of existing systems
    - Innovation and creative renewal of business models and practices
    - Exploration of new opportunities and possibilities
    - Transformation and fundamental change of organizational structures
    
    Organizations need to balance these different modes to address short-term performance requirements while ensuring long-term sustainability and growth.
    
    ## Management Processes
    
    The SGMM identifies several core management processes that are essential for organizational effectiveness:
    
    - **Normative Management**: Establishing values, principles, and norms that guide organizational behavior
    - **Strategic Management**: Developing and implementing strategies that secure the organization's long-term success
    - **Operational Management**: Ensuring efficient and effective execution of day-to-day activities
    
    These processes need to be integrated and aligned to create a coherent management system.
    
    ## Conclusion
    
    The St. Gallen Management Model provides a comprehensive framework for understanding and designing management systems. By taking a holistic and integrated approach, it helps managers navigate the complexity of modern organizations and develop strategies and structures that are responsive to environmental conditions and stakeholder expectations.
    """
    
    metadata = {
        "source": "St. Gallen Management Model Textbook",
        "authors": "University of St. Gallen Faculty",
        "year": 2023,
        "keywords": ["management", "strategy", "organizational design", "stakeholder management"],
        "is_sample": True
    }
    
    # Create document
    document_id = Document.create(title, content, metadata)
    
    if document_id:
        print(f"Sample document created with ID: {document_id}")
        return document_id
    else:
        print("Failed to create sample document")
        return None

def create_context_templates():
    """Create default context templates for personalization"""
    
    print("Creating context templates...")
    
    # Company profile template
    company_profile = {
        "name": "Company Profile",
        "description": "Profile parameters for the company or organization",
        "parameters": {
            "company_size": {
                "type": "select",
                "options": ["small", "medium", "large", "enterprise"],
                "default": "medium",
                "description": "Size of the company or organization"
            },
            "maturity_stage": {
                "type": "select",
                "options": ["startup", "growth", "maturity", "renewal", "decline"],
                "default": "growth",
                "description": "Current stage in the organizational lifecycle"
            },
            "industry": {
                "type": "select",
                "options": ["technology", "healthcare", "finance", "manufacturing", "retail", "services", "education", "government", "other"],
                "default": "technology",
                "description": "Primary industry sector"
            },
            "legal_form": {
                "type": "select",
                "options": ["corporation", "llc", "partnership", "nonprofit", "government", "other"],
                "default": "corporation",
                "description": "Legal form of the organization"
            }
        }
    }
    
    # Management role template
    management_role = {
        "name": "Management Role",
        "description": "Role parameters for the decision maker",
        "parameters": {
            "management_level": {
                "type": "select",
                "options": ["board", "executive", "middle", "operational"],
                "default": "executive",
                "description": "Level of management responsibility"
            },
            "functional_area": {
                "type": "select",
                "options": ["general", "finance", "marketing", "operations", "hr", "it", "rd", "legal", "other"],
                "default": "general",
                "description": "Primary functional area of responsibility"
            },
            "decision_authority": {
                "type": "select",
                "options": ["strategic", "tactical", "operational"],
                "default": "strategic",
                "description": "Level of decision-making authority"
            }
        }
    }
    
    # Management challenge template
    management_challenge = {
        "name": "Management Challenge",
        "description": "Current management challenge being addressed",
        "parameters": {
            "challenge_type": {
                "type": "select",
                "options": ["growth", "innovation", "transformation", "optimization", "crisis", "governance", "sustainability", "digital", "other"],
                "default": "growth",
                "description": "Type of management challenge"
            },
            "timeframe": {
                "type": "select",
                "options": ["immediate", "short_term", "medium_term", "long_term"],
                "default": "medium_term",
                "description": "Timeframe for addressing the challenge"
            },
            "complexity": {
                "type": "select", 
                "options": ["low", "medium", "high", "very_high"],
                "default": "medium",
                "description": "Complexity level of the challenge"
            }
        }
    }
    
    # Environmental context template
    environmental_context = {
        "name": "Environmental Context",
        "description": "External environment parameters",
        "parameters": {
            "market_dynamics": {
                "type": "select",
                "options": ["stable", "evolving", "disruptive", "volatile"],
                "default": "evolving",
                "description": "Current state of market dynamics"
            },
            "technological_intensity": {
                "type": "select",
                "options": ["low", "medium", "high", "cutting_edge"],
                "default": "medium",
                "description": "Level of technological intensity"
            },
            "regulatory_density": {
                "type": "select",
                "options": ["low", "medium", "high", "very_high"],
                "default": "medium",
                "description": "Density of regulatory requirements"
            },
            "global_orientation": {
                "type": "select",
                "options": ["local", "regional", "international", "global"],
                "default": "regional",
                "description": "Geographic scope of operations"
            }
        }
    }
    
    # Create the templates
    templates = [company_profile, management_role, management_challenge, environmental_context]
    
    for template in templates:
        template_id = Context.create(template["name"], template["description"], template["parameters"])
        if template_id:
            print(f"Created template '{template['name']}' with ID: {template_id}")
        else:
            print(f"Failed to create template '{template['name']}'")

def initialize_database():
    """Initialize the database with sample data and process for embeddings"""
    try:
        # Create sample document
        document_id = create_sample_document()
        
        if document_id:
            # Process document for vector embeddings
            embeddings_service = EmbeddingsService()
            success = embeddings_service.process_document(document_id)
            
            if success:
                print("Successfully processed document for embeddings")
            else:
                print("Failed to process document for embeddings")
        
        # Create context templates
        create_context_templates()
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

if __name__ == "__main__":
    initialize_database() 
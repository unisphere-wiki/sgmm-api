import os
import sys
import argparse
import json
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.ocr_service import MistralOCRService
from app.services.embeddings_service import EmbeddingsService

def import_book(pdf_path, title=None, metadata=None):
    """Import a PDF book into the system"""
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return False
        
    if not pdf_path.lower().endswith('.pdf'):
        print("Error: Only PDF files are supported")
        return False
    
    # Use filename as title if not provided
    if title is None:
        title = os.path.basename(pdf_path).rsplit('.', 1)[0]
    
    # Default metadata
    if metadata is None:
        metadata = {
            "source": "Imported Book",
            "type": "textbook"
        }
    
    print(f"Importing book: {title} from {pdf_path}")
    
    # Initialize services
    ocr_service = MistralOCRService()
    
    # Process document
    print("Extracting text...")
    try:
        document_id = ocr_service.process_document(pdf_path, title, metadata)
        
        if not document_id:
            print("Error: Failed to process document")
            return False
        
        # Generate embeddings
        try:
            print("Generating embeddings (this may take a while)...")
            embedding_service = EmbeddingsService()
            success = embedding_service.process_document(document_id)
            
            if not success:
                print("Error: Failed to generate embeddings, but document was processed")
                return document_id
                
        except Exception as e:
            print(f"Warning: Failed to generate embeddings due to: {str(e)}")
            print("The document was processed but embeddings could not be generated.")
            # Create a local backup of the imported PDF
            backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'imported_books')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_pdf_path = os.path.join(backup_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, backup_pdf_path)
            
            # Save metadata
            metadata_path = os.path.join(backup_dir, f"{os.path.basename(pdf_path)}.meta.json")
            with open(metadata_path, 'w') as f:
                json.dump({
                    "title": title,
                    "metadata": metadata,
                    "original_path": pdf_path
                }, f, indent=2)
                
            print(f"Created backup of the book at {backup_pdf_path}")
            return document_id
            
        print(f"Successfully imported book with ID: {document_id}")
        return document_id
        
    except Exception as e:
        print(f"Error during document processing: {str(e)}")
        # Create a local backup of the imported PDF
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'imported_books')
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_pdf_path = os.path.join(backup_dir, os.path.basename(pdf_path))
        shutil.copy2(pdf_path, backup_pdf_path)
        
        # Save metadata
        metadata_path = os.path.join(backup_dir, f"{os.path.basename(pdf_path)}.meta.json")
        with open(metadata_path, 'w') as f:
            json.dump({
                "title": title,
                "metadata": metadata,
                "original_path": pdf_path
            }, f, indent=2)
            
        print(f"Created backup of the book at {backup_pdf_path}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import a PDF book into the SGMM system')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--title', help='Title of the book (defaults to filename)')
    parser.add_argument('--author', help='Author of the book')
    parser.add_argument('--year', help='Publication year', type=int)
    
    args = parser.parse_args()
    
    metadata = {
        "source": "Imported Book"
    }
    
    if args.author:
        metadata["author"] = args.author
        
    if args.year:
        metadata["year"] = args.year
    
    import_book(args.pdf_path, args.title, metadata) 
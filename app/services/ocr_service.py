import base64
import requests
import json
import os
import tempfile
import PyPDF2
from pdf2image import convert_from_path
from app.config import MISTRAL_API_KEY
from app.models.db_models import Document

class MistralOCRService:
    """Service to process documents using Mistral AI's OCR capabilities"""
    
    def __init__(self):
        self.api_key = MISTRAL_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.api_url = "https://api.mistral.ai/v1/ocr"
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF document using PyPDF2 first, falling back to OCR if needed
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # First try to extract text directly using PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract text from each page
                full_text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    
                    # If page has text, add it to the full text
                    if page_text and page_text.strip():
                        full_text += f"\n\n--- Page {i+1} ---\n\n"
                        full_text += page_text
                    else:
                        # If page has no extractable text, it might need OCR
                        # Here we would convert page to image and use OCR
                        # This is a placeholder for that logic
                        page_image = self._convert_pdf_page_to_image(pdf_path, i)
                        if page_image:
                            ocr_text = self._extract_text_from_image(page_image)
                            if ocr_text:
                                full_text += f"\n\n--- Page {i+1} ---\n\n"
                                full_text += ocr_text
                            # Clean up temporary image file
                            os.remove(page_image)
            
            return full_text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def _convert_pdf_page_to_image(self, pdf_path, page_num):
        """
        Convert a PDF page to an image for OCR processing
        
        Args:
            pdf_path (str): Path to the PDF file
            page_num (int): Page number to convert
            
        Returns:
            str: Path to the temporary image file
        """
        try:
            # Create a temporary file to store the image
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_file.close()
            
            # Convert the specific page to an image
            images = convert_from_path(
                pdf_path, 
                first_page=page_num+1,  # pdf2image uses 1-based indexing
                last_page=page_num+1,
                dpi=300,  # Higher DPI for better OCR results
                fmt='jpeg',
                thread_count=1
            )
            
            if not images:
                os.unlink(temp_file.name)  # Clean up if conversion failed
                return None
            
            # Save the image to the temporary file
            images[0].save(temp_file.name, 'JPEG')
            
            # Return the path to the temporary image file
            return temp_file.name
        except Exception as e:
            print(f"Error converting PDF page to image: {str(e)}")
            if 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)  # Clean up on error
            return None
    
    def _extract_text_from_image(self, image_path):
        """
        Extract text from an image file using Mistral AI OCR
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Prepare the payload
            payload = {
                "image": {
                    "data": image_data
                },
                "options": {
                    "language": "auto",
                    "format": "text"
                }
            }
            
            # Make the API request
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Extract text from response
            result = response.json()
            extracted_text = result["text"]
            
            return extracted_text
            
        except Exception as e:
            print(f"Error extracting text from image: {str(e)}")
            return None
    
    def process_document(self, document_path, title, metadata=None):
        """
        Process a document and store it in the database
        
        Args:
            document_path (str): Path to the document file (PDF)
            title (str): Document title
            metadata (dict, optional): Additional metadata for the document
            
        Returns:
            str: Document ID if successful, None otherwise
        """
        try:
            # Check if file is a PDF
            if document_path.lower().endswith('.pdf'):
                full_text = self.extract_text_from_pdf(document_path)
            else:
                # For other file types, might need different processing
                print(f"Unsupported document type: {document_path}")
                return None
            
            if not full_text:
                return None
                
            # Store the document in the database
            if metadata is None:
                metadata = {}
            
            # Add file information to metadata
            file_name = os.path.basename(document_path)
            metadata["file_name"] = file_name
            metadata["file_type"] = os.path.splitext(file_name)[1]
            
            document_id = Document.create(title, full_text, metadata)
            
            return document_id
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None 
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pytesseract
from PIL import Image
import re
import spacy
import chardet
from typing import List, Optional
import tempfile
import logging

# PDF text extraction
import PyPDF2

# Additional document handling
import docx
import csv
import openpyxl
from datetime import datetime

class WebScraper:
    def __init__(self, 
                 url: str, 
                 base_output_dir: str = tempfile.gettempdir(),
                 extract_text: bool = False,
                 extract_links: bool = False,
                 extract_documents: bool = False,
                 extract_images: bool = False):
        """
        Initialize the web scraper with precise extraction control
        
        :param url: Target webpage URL
        :param base_output_dir: Base directory for saving scraped content
        :param extract_text: Flag to extract webpage text
        :param extract_links: Flag to extract hyperlinks
        :param extract_documents: Flag to download documents
        :param extract_images: Flag to download images
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Core configuration
        self.url = url
        self.BeautifulSoup = BeautifulSoup
        
        # Strict extraction flags
        self.extract_text = extract_text
        self.extract_link = extract_links
        self.extract_documents = extract_documents
        self.extract_images = extract_images
        
        # Create safe, unique folder name
        self.safe_folder_name = self._create_safe_folder_name(url)
        
        # Create output paths
        self.output_dir = os.path.join(base_output_dir, self.safe_folder_name)
        self.links_dir = os.path.join(self.output_dir, 'links')
        self.docs_dir = os.path.join(self.output_dir, 'documents')
        self.images_dir = os.path.join(self.output_dir, 'images')
        
        # Conditionally create directories only if extraction is enabled
        if self.extract_link:
            os.makedirs(self.links_dir, exist_ok=True)
        if self.extract_documents:
            os.makedirs(self.docs_dir, exist_ok=True)
        if self.extract_images:
            os.makedirs(self.images_dir, exist_ok=True)
        if self.extract_text:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Load spaCy model for text processing
        self._load_spacy_model()

    def _load_spacy_model(self):
        """
        Load or download spaCy English model
        """
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            self.logger.info("Downloading spaCy English model...")
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

    def _create_safe_folder_name(self, url: str) -> str:
        """
        Create a safe, unique folder name from URL
        """
        safe_name = url.replace('https://', '').replace('http://', '')
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in ['-', '_'])
        
        # Add timestamp (using ISO format for readability and filesystem compatibility)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Combine safe name and timestamp
        full_safe_name = f"{safe_name[:20]}_{timestamp}"
        return full_safe_name

    def fetch_page_content(self):
        """
        Fetch webpage content with robust error handling
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Webpage fetch failed: {e}")
            return None
        
    def detect_encoding(self, filepath: str) -> str:
        """
        Detect the encoding of a file
        
        :param filepath: Path to the file
        :return: Detected encoding
        """
        with open(filepath, 'rb') as file:
            result = chardet.detect(file.read())
        return result['encoding'] or 'utf-8'

    def extract_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Selectively extract links based on configuration
        """
        if not self.extract_link:
            return []

        links = set()
        base_url = urllib.parse.urlparse(self.url).scheme + "://" + urllib.parse.urlparse(self.url).netloc
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urllib.parse.urljoin(base_url, href)
            links.add(full_url)
        
        return list(links)

    def save_links(self, links: List[str]):
        """
        Save extracted links with strict extraction control
        """
        if not self.extract_link:
            return 0
        saved_link = 0
        links_file = os.path.join(self.links_dir, 'links.txt')
        try:
            with open(links_file, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(f"{link}\n")
                    saved_link += 1
            self.logger.info(f"Saved {len(links)} links")
        except Exception as e:
            self.logger.error(f"Link saving failed: {e}")
        return saved_link

    def download_documents(self, soup: BeautifulSoup):
        """
        Strictly download documents only if enabled
        """
        if not self.extract_documents:
            return 0

        doc_extensions = ['.pdf', '.docx', '.doc', '.txt', '.csv', '.xls', '.xlsx']
        base_url = urllib.parse.urlparse(self.url).scheme + "://" + urllib.parse.urlparse(self.url).netloc
        
        documents_downloaded = 0
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urllib.parse.urljoin(base_url, href)
            
            if any(ext in href.lower() for ext in doc_extensions):
                try:
                    doc_response = requests.get(full_url, timeout=5)
                    filename = os.path.join(self.docs_dir, os.path.basename(href))
                    
                    with open(filename, 'wb') as f:
                        f.write(doc_response.content)
                    
                    documents_downloaded += 1
                    self.extract_text_from_document(filename)
                except Exception as e:
                    self.logger.warning(f"Document download failed: {e}")
        
        self.logger.info(f"Downloaded {documents_downloaded} documents")
        return documents_downloaded
        
    def extract_text_from_document(self, filepath: str):
        """
        Extract text from various document types with robust encoding handling
        
        :param filepath: Path to the document file
        """
        # If document extraction is disabled, skip
        if not self.extract_documents:
            return

        try:
            # Get file extension
            file_ext = os.path.splitext(filepath)[1].lower()

            # PDF extraction
            if file_ext == '.pdf':
                text = self.extract_pdf_text(filepath)
            
            # DOCX extraction
            elif file_ext in ['.docx', '.doc']:
                text = self.extract_docx_text(filepath)
            
            # CSV extraction
            elif file_ext == '.csv':
                text = self.extract_csv_text(filepath)
            
            # Excel extraction
            elif file_ext in ['.xls', '.xlsx']:
                text = self.extract_excel_text(filepath)
            
            # Plain text
            elif file_ext == '.txt':
                # Detect encoding and read file
                encoding = self.detect_encoding(filepath)
                with open(filepath, 'r', encoding=encoding) as f:
                    text = f.read()
            
            else:
                print(f"Unsupported file type: {file_ext}")
                return

            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Save text to file
            text_filename = os.path.join(self.docs_dir, f"{os.path.splitext(os.path.basename(filepath))[0]}.txt")
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
        
        except Exception as e:
            print(f"Error extracting text from document {filepath}: {e}")

    def extract_pdf_text(self, filepath: str) -> str:
        """
        Extract text from PDF file
        
        :param filepath: Path to PDF file
        :return: Extracted text
        """
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    def extract_docx_text(self, filepath: str) -> str:
        """
        Extract text from DOCX file
        
        :param filepath: Path to DOCX file
        :return: Extracted text
        """
        doc = docx.Document(filepath)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def extract_csv_text(self, filepath: str) -> str:
        """
        Extract text from CSV file
        
        :param filepath: Path to CSV file
        :return: Extracted text
        """
        text = []
        encoding = self.detect_encoding(filepath)
        with open(filepath, 'r', encoding=encoding) as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                text.append(" ".join(row))
        return "\n".join(text)

    def extract_excel_text(self, filepath: str) -> str:
        """
        Extract text from Excel file
        
        :param filepath: Path to Excel file
        :return: Extracted text
        """
        text = []
        workbook = openpyxl.load_workbook(filepath)
        for sheet in workbook.worksheets:
            for row in sheet.iter_rows(values_only=True):
                text.append(" ".join(str(cell) for cell in row if cell is not None))
        return "\n".join(text)

    def download_images(self, soup: BeautifulSoup):
        """
        Strictly download images only if enabled
        """
        if not self.extract_images:
            return 0

        base_url = urllib.parse.urlparse(self.url).scheme + "://" + urllib.parse.urlparse(self.url).netloc
        
        images_downloaded = 0
        for img_tag in soup.find_all('img', src=True):
            img_url = img_tag['src']
            full_img_url = urllib.parse.urljoin(base_url, img_url)
            
            try:
                img_response = requests.get(full_img_url, timeout=5)
                filename = os.path.join(self.images_dir, os.path.basename(img_url))
                
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                
                images_downloaded += 1
                    
                self.extract_text_from_image(filename)
            except Exception as e:
                self.logger.warning(f"Image download failed: {e}")
        
        self.logger.info(f"Downloaded {images_downloaded} images")
        return images_downloaded
        
    def extract_text_from_image(self, filepath: str):
        """
        Extract text from image using OCR
        
        :param filepath: Path to the image file
        """
        # If image extraction is disabled, skip
        if not self.extract_images:
            return

        try:
            # Ensure Tesseract is installed
            text = pytesseract.image_to_string(Image.open(filepath))
            
            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Save text to file
            text_filename = os.path.join(self.images_dir, f"{os.path.splitext(os.path.basename(filepath))[0]}.txt")
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
        except Exception as e:
            print(f"Error extracting text from image {filepath}: {e}")
            
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text using spaCy
        Remove HTML tags, scripts, and unnecessary whitespace
        
        :param text: Input text to clean
        :return: Cleaned text
        """
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract clean text
        cleaned_text = ' '.join([token.text for token in doc if not token.is_space])
        
        return cleaned_text

    def save_webpage_text(self, soup: BeautifulSoup):
        """
        Save webpage text with strict extraction control
        """
        if not self.extract_text:
            return "Text not extracted."

        try:
            # Extract plain text
            text = soup.get_text(separator=' ', strip=True)
            
            # Optional: Clean text using spaCy
            doc = self.nlp(text)
            cleaned_text = ' '.join([token.text for token in doc if not token.is_space])
            
            # Save text
            text_file = os.path.join(self.output_dir, 'webpage_text.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            self.logger.info("Webpage text extracted successfully")
            return "Text extracted."
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            

    def scrape(self):
        """
        Comprehensive scraping method with strict selective extraction
        """
        self.logger.info(f"Starting scrape for URL: {self.url}")
        
        # Confirm extraction options
        self.logger.info(f"Extraction Options - Text: {self.extract_text}, "
                         f"Links: {self.extract_link}, "
                         f"Documents: {self.extract_documents}, "
                         f"Images: {self.extract_images}")
        
        # Fetch webpage
        response = self.fetch_page_content()
        if not response:
            self.logger.error("Scraping failed: Could not fetch webpage")
            return
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        Summary = []
        # Selective extraction
        if self.extract_link:
            links = self.extract_links(soup)
            Summary.append(f"Link Extracted: {self.save_links(links)}")

        if self.extract_documents:
            Summary.append(f"Document Downloaded: {self.download_documents(soup)}")
        
        if self.extract_images:
            Summary.append(f"Images Downloaded: {self.download_images(soup)}")
        
        if self.extract_text:
            Summary.append(self.save_webpage_text(soup))
        
        self.logger.info("Scraping completed successfully")
        return Summary

# def main():
#     """
#     Example usage for standalone script
#     """
#     url = input("Enter URL to scrape: ")
    
#     scraper = WebScraper(
#         url,
#         extract_text=True,     # Set to False to disable
#         extract_links=True,    # Set to False to disable
#         extract_documents=True,  # Set to False to disable
#         extract_images=True     # Set to False to disable
#     )
    
#     scraper.scrape()

# # if __name__ == "__main__":
# #     main()
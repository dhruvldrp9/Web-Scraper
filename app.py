import os
import shutil
import tempfile
import streamlit as st
import validators
from bs4 import BeautifulSoup

# Import the WebScraper class from the existing script
from Web_Scrapper import WebScraper

def validate_url(url):
    """
    Validate the input URL
    """
    return validators.url(url)

def create_zip_file(directory):
    """
    Create a zip file of the given directory
    
    :param directory: Path to the directory to be zipped
    :return: Path to the created zip file
    """
    # Create a unique zip filename
    zip_filename = f"{os.path.basename(directory)}_scraped_data.zip"
    zip_filepath = os.path.join(tempfile.gettempdir(), zip_filename)
    
    # Create zip file
    shutil.make_archive(zip_filepath[:-4], 'zip', directory)
    
    return zip_filepath

def main():
    """
    Streamlit main application
    """
    # Set page configuration
    st.set_page_config(
        page_title="Web Scraper", 
        page_icon=":spider_web:", 
        layout="wide"
    )

    # Title and description
    st.title("🕸️ Web Scraper")
    st.markdown("""
    ### Customize Your Web Scraping
    - Choose what content you want to extract
    - Scrape selectively or comprehensively
    """)

    # URL Input
    url = st.text_input("Enter the URL to scrape:", placeholder="https://example.com")
    
    # Extraction Options
    st.subheader("Select Extraction Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        extract_text = st.checkbox("Extract Text", value=True)
    with col2:
        extract_links = st.checkbox("Extract Links", value=True)
    with col3:
        extract_documents = st.checkbox("Extract Documents", value=True)
    with col4:
        extract_images = st.checkbox("Download Images", value=True)
    
    # Scrape button
    if st.button("Scrape Website"):
        # Validate URL
        if not url:
            st.error("Please enter a valid URL")
            return
        
        if not validate_url(url):
            st.error("Invalid URL. Please enter a complete and valid URL.")
            return
        
        # Validate at least one extraction option is selected
        if not any([extract_text, extract_links, extract_documents, extract_images]):
            st.error("Please select at least one extraction option")
            return
        
        # Show progress
        with st.spinner('Scraping website...'):
            try:
                # Create base output directory in temp folder
                base_output_dir = tempfile.gettempdir()
                
                # Initialize and run scraper
                scraper = WebScraper(
                    url, 
                    extract_text=extract_text,     # From Streamlit checkbox
                    extract_links=extract_links,   # From Streamlit checkbox
                    extract_documents=extract_documents,  # From Streamlit checkbox
                    extract_images=extract_images   # From Streamlit checkbox
                )
                
                
                # Selective scraping based on user choices
                scraping_summary = scraper.scrape()
                
                # Create zip of scraped content
                zip_filepath = create_zip_file(scraper.output_dir)
                
                # Provide download button
                with open(zip_filepath, 'rb') as zip_file:
                    st.success(f"Scraping completed for {url}")
                    
                    # Display scraping summary
                    st.write("### Scraping Summary")
                    for summary_item in scraping_summary:
                        st.info(summary_item)
                    
                    st.download_button(
                        label="Download Scraped Data",
                        data=zip_file,
                        file_name=os.path.basename(zip_filepath),
                        mime='application/zip'
                    )
                
                # Optional: Show extracted text preview if text extraction was selected
                if extract_text:
                    text_file = os.path.join(scraper.output_dir, 'text.txt')
                    if os.path.exists(text_file):
                        with open(text_file, 'r', encoding='utf-8') as f:
                            preview_text = f.read()[:1000]  # First 1000 chars
                        st.write("### Text Extraction Preview")
                        st.text_area("Extracted Text Preview", preview_text, height=200)
            
            except Exception as e:
                st.error(f"An error occurred during scraping: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("Web Scraper | Built by Dhruvkumar")

if __name__ == "__main__":
    main()

# Additional notes for the requirements:
# Ensure the same requirements.txt as before is used

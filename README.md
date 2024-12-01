# 🕸️ Web Scraper

## Overview

The Web Scraper is a powerful, flexible Python-based web scraping tool that allows users to extract various types of content from websites with granular control. Built using Streamlit, this application provides an intuitive web interface for web scraping tasks.

## Features

### 🔍 Comprehensive Extraction Options
- **Text Extraction**: Capture and clean webpage text
- **Link Extraction**: Collect and save hyperlinks from the webpage
- **Document Download**: Automatically download PDF, DOCX, CSV, and Excel files
- **Image Download**: Save images and perform OCR text extraction

### 🛡️ Robust Design
- Intelligent encoding detection
- Strict error handling
- Logging for tracking scraping activities
- Safe folder and filename generation

### 💡 Key Technologies
- Beautiful Soup for HTML parsing
- spaCy for advanced text processing
- PyTesseract for image text extraction
- Streamlit for web application interface

## Prerequisites

### System Requirements
- Python 3.8+
- Tesseract OCR installed
- SpaCy English language model

### Dependencies
Install required libraries using:
```bash
pip install -r Requirements.txt
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/selective-web-scraper.git
cd selective-web-scraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
- Windows: Download from official website
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

## Usage

### Running the Application
```bash
streamlit run app.py
```

### Web Interface
1. Enter the URL you want to scrape
2. Select extraction options:
   - Extract Text
   - Extract Links
   - Extract Documents
   - Extract Images
3. Click "Scrape Website"
4. Download the scraped data as a ZIP file

## Logging

The application provides detailed logging to track scraping activities. Logs include:
- Scraping start and end times
- Number of items extracted
- Any errors encountered

## Security and Ethical Considerations

- Respect website terms of service
- Be aware of robots.txt restrictions
- Use web scraping responsibly
- Avoid overloading servers with rapid requests

## Troubleshooting

### Common Issues
- Ensure URL is valid and accessible
- Check internet connection
- Verify Tesseract OCR installation
- Update SpaCy language model if needed

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

Dhruvkumar - [[Your Contact Information]](https://www.linkedin.com/in/dhruvp9/)

---

**Happy Web Scraping! 🕷️📊**

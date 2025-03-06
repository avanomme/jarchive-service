import os
import gdown
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_tsv():
    """Download the TSV file from Google Drive."""
    try:
        # Google Drive file ID for the TSV file
        file_id = "1rQZsuxqfcMjTKeztIeQGJkiQciirOz9v"
        
        # Download the file
        logger.info("Downloading TSV file from Google Drive...")
        url = f"https://drive.google.com/uc?id={file_id}"
        output = "combined_season1-40.tsv"
        gdown.download(url, output, quiet=False)
        logger.info("TSV file downloaded successfully!")
        
    except Exception as e:
        logger.error(f"Error downloading TSV file: {str(e)}")
        raise

if __name__ == "__main__":
    download_tsv() 
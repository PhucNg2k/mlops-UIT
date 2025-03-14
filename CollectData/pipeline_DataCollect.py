import os
import subprocess
import time

def run_pipeline():
    """
    Run the complete pipeline:
    1. crawl_url.py - Download HTML files from URLs
    2. extract_content.py - Extract content from HTML files
    3. post_process_text.py - Post-process the extracted content
    """
    print("=" * 50)
    print("Starting Content Extraction Pipeline")
    print("=" * 50)
    
    # Step 1: Crawl URLs
    print("\nStep 1: Crawling URLs...")
    try:
        subprocess.run(["python", "crawl_url.py"], check=True)
        print("URL crawling completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during URL crawling: {e}")
        return
    
    # Pause between steps
    time.sleep(1)
    
    # Step 2: Extract content
    print("\nStep 2: Extracting content from HTML files...")
    try:
        subprocess.run(["python", "extract_content.py"], check=True)
        print("Content extraction completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during content extraction: {e}")
        return
    
    # Pause between steps
    time.sleep(1)
    
    # Step 3: Post-process text
    print("\nStep 3: Post-processing text files...")
    try:
        subprocess.run(["python", "post_process_text.py"], check=True)
        print("Post-processing completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during post-processing: {e}")
        return
    
    print("\n" + "=" * 50)
    print("Pipeline completed successfully!")
    print("=" * 50)
    
    # Count the number of files processed
    from constant import HTML_FOLDER, CONTENT_FOLDER
    html_count = sum(1 for _ in os.scandir(HTML_FOLDER) if _.is_file() and _.name.endswith('.html'))
    txt_count = sum(1 for _ in os.scandir(CONTENT_FOLDER) if _.is_file() and _.name.endswith('.txt'))
    
    print(f"\nProcessed {html_count} HTML files and created {txt_count} text files.")
    print(f"Content files are available in the '{CONTENT_FOLDER}' directory.")

if __name__ == "__main__":
    run_pipeline()
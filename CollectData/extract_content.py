import os
from constant import HTML_FOLDER, CONTENT_FOLDER
from bs4 import BeautifulSoup

def main():
    os.makedirs(CONTENT_FOLDER, exist_ok=True)

    # Process each HTML file
    for html_file in os.scandir(HTML_FOLDER):
        if html_file.is_file() and html_file.name.endswith('.html'):
            file_name = html_file.path.split("\\")[-1].split(".")[0]
            dest_path = os.path.join(CONTENT_FOLDER, f"{file_name}.txt")
            
            # Extract content from HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, "html.parser")
                content_div = soup.find("div", class_="content")
                
                if content_div:
                    # Extract title
                    title_element = content_div.find("h2", class_="sub-title")
                    if not title_element:
                        title_element = content_div.find("h1", class_="title")
                    title = title_element.text.strip() if title_element else "No title found"

                    # Write title and content to destination file
                    with open(dest_path, 'w', encoding="utf-8") as dest_f:
                        #dest_f.write(f"{title}\n\n")

                        # Process all paragraphs
                        for element in content_div.find_all(['p']):
                            # Skip paragraphs with unwanted characteristics
                            if any([
                                element.get("class"),  # Skip if has class
                                element.parent and element.parent.name == 'li',  # Skip if inside list item
                                element.parent and element.parent.get('class') and any(c in ['overflow', 'ads', 'social', 'share', 'paging', 'box-star'] for c in element.parent.get('class', [])),  # Skip if parent has unwanted class
                            ]):
                                continue

                            # Get text and filter unwanted content
                            text = element.get_text(strip=True)
                            if text and not any(x in text.lower() for x in ['quảng cáo', 'shopee', 'zalo', 'download', 'app vietjack', 'tải app']):
                                dest_f.write(f"{text}\n\n")
                        
                        '''
                        # Also add important headings that aren't the title
                        for heading in content_div.find_all(['h2', 'h3']):
                            if heading != title_element:  # Skip the title we already added
                                text = heading.get_text(strip=True)
                                if text:
                                    dest_f.write(f"{text}\n\n")
                        '''

                    print(f"Successfully created content file: {dest_path}")
                else:
                    print(f"No content div found in {html_file.path}")

if __name__ == "__main__":
    main()
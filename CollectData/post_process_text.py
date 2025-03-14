import os
import re
from constant import CONTENT_FOLDER

def post_process():
    """
    Process text files in the CONTENT_FOLDER to make them more compact by:
    1. Preserving section headers and their formatting
    2. Removing excessive newlines
    3. Preserving paragraph structure
    4. Removing "Xem thêm" sections and other unneeded content at the end
    """
    # Process each text file in the CONTENT_FOLDER
    for txt_file in os.scandir(CONTENT_FOLDER):
        if txt_file.is_file() and txt_file.name.endswith('.txt'):
            file_path = txt_file.path
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process the content
            processed_content = process_content(content)
            
            # Write the processed content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print(f"Processed file: {txt_file.name}")

def process_content(content):
    """Process the content to make it more compact."""
    # Split content into lines
    lines = content.split('\n')
    processed_lines = []
    
    # Variables to track state
    current_section = None
    skip_mode = False
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Check for "Xem thêm" sections which usually mark the end of useful content
        if "Xem thêm" in line or "Nếu thấy hay" in line:
            skip_mode = True
            continue
            
        if skip_mode:
            continue
            
        # Detect section headers (I., II., a), b), etc.)
        if re.match(r'^[IVX]+\.', line) or re.match(r'^[a-z]\)', line):
            # Add a blank line before new sections (except for the first section)
            if processed_lines:
                processed_lines.append('')
            current_section = line
            processed_lines.append(line)
            continue
            
        # Check if line starts with bullet points
        if line.strip().startswith('+') or line.strip().startswith('-'):
            processed_lines.append(line)
            continue
            
        # Handle normal paragraph text
        # If previous line wasn't a section header or bullet point, append to that line
        if processed_lines and not (
            re.match(r'^[IVX]+\.', processed_lines[-1]) or 
            re.match(r'^[a-z]\)', processed_lines[-1]) or
            processed_lines[-1].strip().startswith('+') or
            processed_lines[-1].strip().startswith('-') or
            processed_lines[-1] == ''
        ):
            processed_lines[-1] += ' ' + line.strip()
        else:
            processed_lines.append(line)
    
    # Join lines with newlines
    return '\n'.join(processed_lines)

if __name__ == "__main__":
    post_process()
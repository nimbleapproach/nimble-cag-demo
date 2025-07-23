import markdown
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .text_splitter import split_text


def process_markdown_file(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """Process a markdown file and return chunks with metadata"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to plain text
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    # Split into chunks
    chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)

    # Create metadata for each chunk
    source_name = file_path.split('/')[-1]  # Get filename
    processed_chunks = []
    
    for j, chunk in enumerate(chunks):
        processed_chunks.append({
            'content': chunk,
            'metadata': {
                "source": source_name,
                "chunk_index": j,
                "file_path": file_path
            },
            'id': f"{source_name}_{j}"
        })
    
    return processed_chunks


def extract_markdown_metadata(content: str) -> Dict[str, Any]:
    """Extract metadata from markdown content (headers, frontmatter, etc.)"""
    metadata = {}
    
    # Extract headers
    lines = content.split('\n')
    headers = []
    
    for line in lines:
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('#').strip()
            headers.append({'level': level, 'title': title})
    
    metadata['headers'] = headers
    
    # Extract frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            # Simple frontmatter parsing (can be enhanced)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
    
    return metadata 
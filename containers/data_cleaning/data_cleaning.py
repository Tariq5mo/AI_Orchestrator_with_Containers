#!/usr/bin/env python3
import sys
import re
import unicodedata

def clean_data(text):
    """
    Clean and normalize text for further processing
    - Normalizes unicode characters
    - Removes special characters and symbols
    - Normalizes whitespace and line breaks
    - Converts text to lowercase for consistency
    - Handles HTML entities and common web artifacts
    - Preserves important sentence structures and formatting
    - Standardizes formatting for lists and common patterns
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

    # Handle HTML entities (like &amp;, &quot;, etc.)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up citation references like [1], [2], etc.
    text = re.sub(r'\[\d+\](?:\[.*?\])?', '', text)

    # Handle section headers that might be from copied web content
    text = re.sub(r'^See also:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^Main article:.*$', '', text, flags=re.MULTILINE)

    # Standardize quotation marks and apostrophes
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)

    # Remove special characters but preserve sentence structure
    text = re.sub(r'[^\w\s\.\,\?\!\:\;\-\(\)\[\]\/\"\']', ' ', text)

    # Handle common abbreviations properly
    text = re.sub(r'(\w)\.(\w)\.', r'\1\2', text)  # Replace e.g. with eg

    # Normalize whitespace, keeping paragraph breaks
    paragraphs = re.split(r'\n\s*\n', text)
    paragraphs = [re.sub(r'\s+', ' ', p).strip() for p in paragraphs]
    text = '\n\n'.join([p for p in paragraphs if p])

    # Detect and preserve list formats
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Convert common list markers to standardized format
        if re.match(r'^\s*[\•\-\*]\s', line):
            lines[i] = '• ' + re.sub(r'^\s*[\•\-\*]\s', '', line)
        # Handle numbered lists
        elif re.match(r'^\s*\d+[\.\)]\s', line):
            lines[i] = re.sub(r'^\s*(\d+)[\.\)]\s', r'\1. ', line)

    text = '\n'.join(lines)

    return text

if __name__ == "__main__":
    # Read from stdin if no arguments provided
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                data = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        data = sys.stdin.read()

    result = clean_data(data)

    # Write to stdout or output file
    if len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'w') as f:
                f.write(result)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(result)

#!/usr/bin/env python3
import sys
import re
import json

def clean_data(text):
    """Remove special characters, extra spaces and normalize text"""
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove special chars
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text.lower()  # Convert to lowercase

if __name__ == "__main__":
    # Read from stdin if no arguments provided
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = f.read()
    else:
        data = sys.stdin.read()
    
    result = clean_data(data)
    
    # Write to stdout or output file
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write(result)
    else:
        print(result)

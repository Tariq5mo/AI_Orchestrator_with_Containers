#!/usr/bin/env python3
import sys
import re
from collections import Counter
import heapq

def clean_citations(text):
    """Remove citation references like [10], [12][dead link]"""
    return re.sub(r'\[\d+\](?:\[.*?\])?', '', text)

def format_lists(text):
    """Convert list-like structures to proper bulleted lists"""
    # Common list patterns in articles
    list_pattern = r'(?:(?:^|\n)([A-Z][a-z]+(?:\s+[a-z]+){1,3})(?:\s+))'
    items = re.findall(list_pattern, text)
    if len(items) > 3:  # If we have multiple short items that look like a list
        formatted_list = "\n• " + "\n• ".join(items)
        # Replace the flat list with a bulleted list
        for item in items:
            text = text.replace(item, "", 1)  # Remove each item (first occurrence only)
        text = re.sub(r'\s{2,}', ' ', text)  # Clean up extra spaces
        text += "\n\n" + formatted_list
    return text

def improve_paragraph_structure(paragraph, max_length=80):
    """Format long paragraphs for better readability"""
    if len(paragraph) <= max_length:
        return paragraph
    # Add line breaks to long paragraphs
    words = paragraph.split()
    lines = []
    current_line = []
    for word in words:
        current_length = sum(len(w) for w in current_line) + len(current_line)
        if current_length + len(word) > max_length:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

def extract_main_topics(text, count=5):
    """Extract main topics from text based on word frequency"""
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    # Remove common stop words
    stop_words = {'the', 'and', 'is', 'in', 'it', 'to', 'of', 'for', 'with', 'as', 'that', 'on', 'at', 'by', 'an', 'be', 'this', 'are'}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    return Counter(filtered_words).most_common(count)

def summarize_text(text, num_sentences=3):
    # Clean and normalize text
    text = clean_citations(text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Split into sentences - more carefully to handle abbreviations
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= num_sentences:
        # For short texts, just format with line breaks
        return "\n\n".join([s for s in sentences if s])

    # Calculate word frequency
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    word_freq = Counter(words)

    # Remove common stop words from consideration
    stop_words = {'the', 'and', 'is', 'in', 'it', 'to', 'of', 'for', 'with', 'as', 'that', 'on', 'at', 'by', 'an', 'be', 'this', 'are'}
    for word in stop_words:
        if word in word_freq:
            del word_freq[word]

    # Normalize word frequency
    max_freq = max(word_freq.values()) if word_freq else 1
    word_freq = {word: freq/max_freq for word, freq in word_freq.items()}

    # Score sentences
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_words = re.sub(r'[^\w\s]', '', sentence.lower()).split()
        sentence_scores[i] = sum(word_freq.get(word, 0) for word in sentence_words)

    # Get top sentences while maintaining original order
    top_indices = heapq.nlargest(num_sentences,
                                range(len(sentences)),
                                key=lambda i: sentence_scores[i])
    top_indices = sorted(top_indices)

    # Build summary from top sentences
    top_sentences = [sentences[i] for i in top_indices]

    # Apply citation cleaning again to ensure all citations are removed
    summary = " ".join(top_sentences)
    summary = clean_citations(summary)

    # Format lists in the summary
    summary = format_lists(summary)

    # Split into paragraphs based on content transitions
    paragraphs = []
    current_paragraph = []
    for sentence in top_sentences:
        current_paragraph.append(sentence)
        # Start a new paragraph after about 2-3 sentences or on topic shift
        if len(current_paragraph) >= 2 and len(" ".join(current_paragraph)) > 150:
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    # Improve each paragraph's structure
    improved_paragraphs = [improve_paragraph_structure(p) for p in paragraphs]

    return "\n\n".join(improved_paragraphs)

if __name__ == "__main__":
    # Read from stdin if no arguments provided
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    # Optional number of sentences parameter (default: 3)
    num_sentences = 3
    if len(sys.argv) > 3:
        try:
            num_sentences = int(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid number of sentences '{sys.argv[3]}'. Using default of 3.", file=sys.stderr)

    # Generate summary
    summary = summarize_text(text, num_sentences)

    # Write to stdout or output file
    if len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'w') as f:
                f.write(summary)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(summary)

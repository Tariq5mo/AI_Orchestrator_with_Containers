#!/usr/bin/env python3
import sys
import re
from collections import Counter
import heapq

def summarize_text(text, num_sentences=3):
    """Extractive summarization based on sentence scoring"""
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= num_sentences:
        return text
    
    # Calculate word frequency
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    word_freq = Counter(words)
    
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
    top_indices.sort()
    
    # Rebuild the summary
    summary = '. '.join([sentences[i] for i in top_indices])
    return summary + '.'

if __name__ == "__main__":
    # Read from stdin if no arguments provided
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = f.read()
    else:
        data = sys.stdin.read()
    
    # Get number of sentences from arguments or default to 3
    num_sentences = 3
    if len(sys.argv) > 3:
        try:
            num_sentences = int(sys.argv[3])
        except:
            pass
    
    result = summarize_text(data, num_sentences)
    
    # Write to stdout or output file
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write(result)
    else:
        print(result)

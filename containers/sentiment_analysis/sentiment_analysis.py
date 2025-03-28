#!/usr/bin/env python3
import sys
import json
import re
from collections import Counter

# Simple sentiment analysis using predefined word lists
# In a real implementation, you might want to use a library like TextBlob or NLTK

POSITIVE_WORDS = set([
    'good', 'great', 'excellent', 'positive', 'wonderful', 'amazing', 'love', 
    'best', 'happy', 'pleasant', 'fantastic', 'perfect', 'better', 'nice'
])

NEGATIVE_WORDS = set([
    'bad', 'terrible', 'awful', 'negative', 'horrible', 'hate', 'worst',
    'poor', 'sad', 'unpleasant', 'disappointing', 'worse', 'problem'
])

def analyze_sentiment(text):
    """Analyze sentiment of the given text"""
    # Normalize and split text
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    word_count = len(words)
    
    # Count positive and negative words
    sentiment_counter = Counter()
    for word in words:
        if word in POSITIVE_WORDS:
            sentiment_counter['positive'] += 1
        elif word in NEGATIVE_WORDS:
            sentiment_counter['negative'] += 1
    
    # Calculate sentiment score (-1 to 1)
    pos_count = sentiment_counter['positive']
    neg_count = sentiment_counter['negative']
    
    if word_count > 0:
        score = (pos_count - neg_count) / max(1, word_count * 0.1)  # Normalize
        score = max(min(score, 1.0), -1.0)  # Clamp between -1 and 1
    else:
        score = 0.0
        
    return {
        'score': score,
        'positive_words': pos_count,
        'negative_words': neg_count,
        'classification': 'positive' if score > 0 else 'negative' if score < 0 else 'neutral'
    }

if __name__ == "__main__":
    # Read from stdin if no arguments provided
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = f.read()
    else:
        data = sys.stdin.read()
    
    result = analyze_sentiment(data)
    
    # Write to stdout or output file
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))

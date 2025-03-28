FROM python:3.9-slim

WORKDIR /app
COPY sentiment_analysis.py /app/
RUN chmod +x /app/sentiment_analysis.py

ENTRYPOINT ["python", "sentiment_analysis.py"]
# Default to using stdin/stdout if no args provided
CMD []

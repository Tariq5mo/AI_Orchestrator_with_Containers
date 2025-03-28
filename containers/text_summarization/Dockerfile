FROM python:3.9-slim

WORKDIR /app
COPY summarize.py /app/
RUN chmod +x /app/summarize.py

ENTRYPOINT ["python", "summarize.py"]
# Default to using stdin/stdout if no args provided
CMD []

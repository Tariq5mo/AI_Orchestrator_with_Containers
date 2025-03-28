FROM python:3.9-slim

WORKDIR /app
COPY data_cleaning.py /app/
RUN chmod +x /app/data_cleaning.py

ENTRYPOINT ["python", "data_cleaning.py"]
# Default to using stdin/stdout if no args provided
CMD []

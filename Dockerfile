FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY extractor ./extractor
COPY static ./static
COPY sample_data ./sample_data

EXPOSE 55555

CMD ["python", "-m", "extractor.webapp"] 
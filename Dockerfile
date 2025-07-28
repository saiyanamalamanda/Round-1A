FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY wheelhouse/ ./wheelhouse/
RUN pip install --no-index --find-links=wheelhouse -r requirements.txt

COPY extract_outline.py .

RUN mkdir input output

CMD ["python", "extract_outline.py"]

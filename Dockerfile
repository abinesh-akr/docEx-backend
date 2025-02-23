FROM python:3.9-slim

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr && apt install -y oppler-utils

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install opencv-python
# Copy the rest of your app
COPY . /app
WORKDIR /app

CMD ["streamlit", "run", "app.py"]

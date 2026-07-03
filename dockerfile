FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y wget curl unzip && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

RUN pip install flask requests beautifulsoup4 selenium webdriver-manager

CMD ["python", "app.py"]
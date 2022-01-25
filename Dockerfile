# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.8

# Install manually all the missing libraries
RUN apt-get update && apt-get install -y python \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
 
# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install Python dependencies.
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

LABEL org.opencontainers.image.source="https://github.com/Suhel-Kap/selenium-web-scraper"

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

ENTRYPOINT [ "python", "app.py" ]
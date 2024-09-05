# TODO(P1, devops): GREAT, after a half day sweating of this Dockerfile I have found that
# AWS Lambda Layers might just get me this out-of-box. MAYBE that is why I could NOT find an example,
# cause everyone is just using that feature :facepalm:
# AWS Lambda Layers: Headless Chrome and Chromium with Puppeteer: These layers are useful for web scraping,
# generating screenshots or PDFs from web pages, etc.

# TOO MUCH CONTEXT HERE:
# https://chat.openai.com/share/7208ab98-4f1a-436c-8d2f-0a101185f0ee
# Use an official Debian runtime as a parent image
FROM debian:buster-slim

# Set the working directory in the container to /app
WORKDIR /app

# Install necessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    python3-pip \
    xvfb \
    libxi6 \
    libgconf-2-4

# Install Chromium Browser
RUN apt-get update && apt-get install -y chromium

# Install ChromeDriver compatible with Chromium
RUN CHROMIUM_VERSION=$(dpkg-query --show --showformat='${Version}' chromium | awk -F'.' '{ print $1 }') \
    && CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROMIUM_VERSION}) \
    && wget -N -q http://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip -P ~/ \
    && unzip ~/chromedriver_linux64.zip -d ~/ \
    && rm ~/chromedriver_linux64.zip \
    && mv -f ~/chromedriver /usr/local/bin/chromedriver \
    && chown root:root /usr/local/bin/chromedriver \
    && chmod 0755 /usr/local/bin/chromedriver


# Test that Chromium and ChromeDriver were installed successfully
# RUN CHROMIUM_VERSION=$(dpkg-query --show --showformat='${Version}' chromium | awk -F'.' '{ print $1 }') \
#    && echo "Chromium version: $CHROMIUM_VERSION" \
#    && chromedriver --version

# Upgrade pip
RUN pip3 install --upgrade pip

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the command when the container launches
CMD [ "python3", "./scraper.py" ]

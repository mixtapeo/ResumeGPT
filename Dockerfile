# Set base image (host OS)
FROM python:3.12-alpine

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app


ENV wildapiricot_api_key=
ENV OPENAI_API_KEY=
ENV account_id=
# Copy the dependencies file to the working directory
COPY requirements.txt .

# Print the contents of requirements.txt for debugging
RUN cat requirements.txt

# Update package manager and install build dependencies
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev curl-dev

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local app directory to the working directory
COPY . .

# Specify the command to run on container start
CMD [ "python", "./app/main.py" ]
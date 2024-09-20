
# Paperless Metadata Ollama Processor

<div style="border: 2px solid red; padding: 10px;">
  <strong>Warning:</strong> This project is under development and might break your data or your paperless-ngx instance. Be sure to have a proper backup strategy in place before using it.
</div>


This project processes metadata for documents in paperless-ngx, leveraging the Ollama API with a model of your choosing for extracting and processing metadata such as title, date, tags, document type, and correspondent.

## Features
- Extracts metadata from documents using a (local) Ollama model.
- Retrieves title, date, tags, document type, and correspondent.
- Prefers paperless-ngx retrieved data, as in only overwrites empty document type and correspondent. Existing document tags are also being kept.
- Can be used as a post-processing step on document consumption. See [Post Processing Hook](#post-processing-hook).
- Can be triggered via API endpoint directly. See [API Usage](#api-usage).


- Many environment variables can be customized. See [Environment Variables](#environment-variables).
- Prompt can be customized. See [Prompt Placeholders](#prompt-placeholders).

## Roadmap

- Support for batch document reprocessing.
- Enable toggles for metadata autocompletion.

## Prerequisites

Before using this project, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Paperless-ngx](https://docs.paperless-ngx.com/)
- [Ollama](https://ollama.com/)
- An Ollama model of choice (by default [gemma2:2b](https://ollama.com/library/gemma2:2b))

Furthermore, the paperless-ngx and ollama instances need to run on the same Docker network.

---

## Quick Start

### Pull the Docker Image from DockerHub

You can pull the pre-built Docker image from DockerHub and run it locally:

```shell
docker pull douaberigoale/paperless-metadata-ollama-processor:latest
```

#### Run the Docker Container

To run the Docker container, you can use the following command. The volume maps the `/data` directory inside the container to a local directory for persistence (such as the logs and prompts):

```shell
docker run -p 5000:5000 \
  -v ./postprocessing:/data \
  -e PAPERLESS_API_TOKEN=<your-paperless-api-token> \
  douaberigoale/paperless-metadata-ollama-processor:latest
```

Otherwise, you can use this docker-compose.yml to run the Docker container:

```dockerfile
services:

  # (... paperless services ...) #

  paperless-metadata-ollama-processor:
    container_name: postprocessor
    image: douaberigoale/paperless-metadata-ollama-processor:latest
    ports:
      - "5000:5000"
    environment:
      - PAPERLESS_API_TOKEN=<your-paperless-api-token>
    volumes:
      - ./postprocessing:/data
    networks:
      - paperless-network

networks:
  paperless-network:
    external: true
```

---

## Environment Variables

You can configure the application with the following environment variables:

- `APP_PORT`: The port the app will run on (default: `5000`).
- `LOG_FILE`: Path to the log file (e.g., `/data/log`).
- `OLLAMA_PROMPT_FILE`: Path to the prompt file (e.g., `/data/prompt`).
- `OLLAMA_MODEL_NAME`: The Ollama model to use (e.g., `gemma2:2b`).
- `OLLAMA_API_URL`: URL for the Ollama API (e.g., `http://ollama:11434/api/generate`).
- `OLLAMA_TRUNCATE_NUMBER`: Number of words to truncate the document to (default: `500`).
- `PAPERLESS_API_URL`: URL for the Paperless-ngx API (e.g., `http://paperless-ngx:8000/api`).
- `PAPERLESS_API_TOKEN`: API token for Paperless-ngx (required).

---

## Prompt Placeholders

You might want to change the prompt located (by default) under /data/prompt with your own. This is possible, but you must take note of the following placeholders:

Note: The prompt file does not get overwritten by the container.

- **`{existing_correspondents}`**: A placeholder for the list of available correspondents in paperless-ngx.
- **`{existing_tags}`**: A placeholder for the list of available tags in paperless-ngx.
- **`{existing_types}`**: A placeholder for the list of available document types in paperless-ngx.
- **`{truncated_text}`**: The OCR text from the document, truncated to a manageable length for processing.

---

## How to Use

This app provides two main ways to process documents and extract metadata: through a **Post Processing Hook** or via the **API**. Below are the details on how to use each method.

### Post Processing Hook

To use the app as a post-processing hook in **paperless-ngx**, you can set up the hook as follows:

Assign the provided Python script as a post-consumption hook in your Paperless-ngx configuration. This will allow the app to process documents automatically once they have been consumed by Paperless.

```docker
  paperless-ngx:
    (...)
    volumes:
      (...)
      - /wherever/this/is/postprocessing:/usr/src/paperless/postprocessing
    environment:
      (...)
      PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/paperless/postprocessing/post_consumption_hook.py
   ```
Note: Edit the script to adjust the port of the postprocessor, if needed.

## API Usage

### GET `/`

- **Description**: This endpoint verifies that the environment variables are correctly set and returns the current configuration.

- **Example**:
  ```shell
  curl -X GET http://localhost:5000/

- **Response**:
  ```json
  {
    "message": "Environment variables validated successfully",
    "app_port": 5000,
    "log_file": "/data/log",
    "ollama_prompt_file": "/data/prompt",
    "ollama_model_name": "gemma2:2b",
    "ollama_api_url": "http://ollama:11434/api/generate",
    "ollama_truncate_number": 500,
    "paperless_api_url": "http://paperless-ngx:8000/api",
    "paperless_api_token": "your-api-token"
  }
  ```


### GET `/process/{doc_id}`

- **Description**: This endpoint verifies that the environment variables are correctly set and returns the current configuration.

- **Example**:
    ```shell
    curl -X GET http://localhost:5000/process/123
    ```
  
- **Response**:
  - On success: HTTP 200
  - On failure: HTTP 500 with a detailed error message
---

## Useful Information

- paperless-ngx, Ollama and the postprocessor (this container) must run in the same Docker network.
- The logs get emptied on every container recreate.

---

## License

This project is licensed under the GNU General Public License (GPL).

---

## Contact

For any questions, feel free to reach out to me, and I'll try to answer as soon as possible. You can send me a message or write one in the issues board.

---

## Disclaimer of Liability

The author of this project assumes no responsibility or liability for any errors or omissions in the content of this service. The information contained in this service is provided on an "as is" basis with no guarantees of completeness, accuracy, usefulness, or timeliness.

By using this project, you agree that the author will not be held liable for any direct, indirect, incidental, or consequential damages arising out of or related to the use of this project. This includes, but is not limited to, data loss, incorrect data processing, security vulnerabilities, or other issues that may result from using this service.

It is your responsibility to review, verify, and validate the code and any data or information processed by this service before relying on it.

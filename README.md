
# Paperless Metadata Ollama Processor

This project processes metadata for documents in Paperless-ngx, leveraging the Ollama API with a model of your choosing for extracting and processing metadata such as titles, tags, and correspondents.
## Features
- Extracts metadata from documents using a (local) Ollama API.
- Processes data such as titles, tags, correspondents, and document types.
- Prompt can be modified to enable usage of different LLMs.
- (Upcoming) Support for batch document reprocessing in terms of titles, tags, correspondents, and document types.
- Meant to be integrated as a post processing step on document consumption, but can be triggered via API as well in both single and (soon) batch mode.  

## Prerequisites

Before using this project, ensure you have the following installed:

- [Paperless-ngx](https://docs.paperless-ngx.com/)
- [Docker](https://www.docker.com/get-started)
- [Ollama](https://ollama.com/)
- An Ollama model of choice (if running Ollama locally)

Furthermore, the paperless-ngx and ollama instances need to run on the same Docker network.

---

## Quick Start

### Pull the Docker Image from DockerHub

You can pull the pre-built Docker image from DockerHub and run it locally:

```bash
docker pull douaberigoale/paperless-metadata-ollama-processor:latest
```

#### Run the Docker Container

To run the Docker container, you can use the following command. The volume maps the `/data` directory inside the container to a local directory for persistence (such as the logs and prompts):

```bash
docker run -p 5000:5000 \
  -v ./data:/data \
  -e APP_PORT=5000 \
  -e LOG_FILE=/data/log \
  -e OLLAMA_PROMPT_FILE=/data/prompt \
  -e OLLAMA_MODEL_NAME=gemma2:2b \
  -e OLLAMA_API_URL=http://ollama:11434/api/generate \
  -e OLLAMA_TRUNCATE_NUMBER=200 \
  -e PAPERLESS_API_URL=http://paperless-ngx:8000/api \
  -e PAPERLESS_API_TOKEN=<your-paperless-api-token> \
  paperless-metadata-ollama-processor
```
---

## Environment Variables

You can configure the application with the following environment variables:

- `APP_PORT`: The port the app will run on (default: `5000`).
- `LOG_FILE`: Path to the log file (e.g., `/data/log`).
- `OLLAMA_PROMPT_FILE`: Path to the prompt file (e.g., `/data/prompt`).
- `OLLAMA_MODEL_NAME`: The Ollama model to use (e.g., `gemma2:2b`).
- `OLLAMA_API_URL`: URL for the Ollama API (e.g., `http://ollama:11434/api/generate`).
- `OLLAMA_TRUNCATE_NUMBER`: Number of words to truncate the document to (default: `200`).
- `PAPERLESS_API_URL`: URL for the Paperless-ngx API (e.g., `http://paperless-ngx:8000/api`).
- `PAPERLESS_API_TOKEN`: API token for Paperless-ngx (required).

---

### How to Use the App

// todo

---

## Contributing

We welcome contributions! Please submit issues or pull requests for new features or bug fixes.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

---

## License

// todo This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any questions, feel free to reach out to me and I'll try to answer as soon as possible.

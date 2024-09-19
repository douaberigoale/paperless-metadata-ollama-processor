#!/usr/bin/env python3

import requests
import sys
import os

def post_consumption_hook():
    if len(sys.argv) < 2:
        sys.exit(1)

    document_id = sys.argv[1]
    api_url = f"http://localhost:{os.getenv('APP_PORT')}/process/{document_id}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        print(f"Document {document_id} processed successfully.")
        sys.exit(0)
    except requests.exceptions.RequestException as e:
        print(f"Error processing document {document_id}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    post_consumption_hook()

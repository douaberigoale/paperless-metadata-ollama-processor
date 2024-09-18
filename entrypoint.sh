#!/bin/sh

# Check if the /data directory exists, if not create it
if [ ! -d "/data" ]; then
  echo "Creating /data directory..."
  mkdir -p /data
fi

# Check if the log file exists, if not create it
if [ ! -f "/data/log" ]; then
  echo "Creating /data/log file..."
  touch /data/log
fi

# Check if the prompt file exists, if not create it with initial content
if [ ! -f "/data/prompt" ]; then
  echo "Creating /data/prompt file with initial content..."
  cat <<EOF > /data/prompt
Extract the title, date, up to 3 tags, correspondent, and document type from the following document in a structured format. The document may be in German, English, or Romanian, and may contain some noise due to OCR. Use the lists provided for correspondents, tags, and document types wherever possible. Only create new entries if none of the existing ones fit, and only extract information if you are certain about it.

For all documents processed with this prompt, add the tag "unverified" in addition to any other relevant tags.

Return only the values in the specified format without providing any explanations, comments, or additional information. If any information is not clearly identifiable, leave the corresponding fields empty.

Return the result in this exact format:

{ "title": "[Title]", "date": "[YYYY-MM-DD]", "tags": ["unverified", "Tag1", "Tag2", "Tag3"], "correspondent": "[Correspondent]", "type": "[Document Type]" }

Here are the existing correspondents, tags, and document types:
Correspondents: {existing_correspondents}
Tags: {existing_tags}
Document Types: {existing_types}

Here is the document text:
"{truncated_text}"
EOF
fi

# Run the FastAPI app with Uvicorn
exec "$@"

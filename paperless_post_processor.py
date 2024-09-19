from services.ollama_service import OllamaService
from services.paperless_service import PaperlessService


class PaperlessPostProcessor:
    def __init__(self, logger, paperless: PaperlessService, ollama: OllamaService):
        self.logger = logger
        self.paperless = paperless
        self.ollama = ollama

    def process_document(self, doc_id):
        try:
            ocr_text = self.paperless.get_document_text(doc_id)
            if not ocr_text:
                self.logger.log(f"No OCR text found for document ID {doc_id}.")
                return

            tags, types, correspondents = self.paperless.get_existing_metadata()
            metadata = self.ollama.call(ocr_text, tags, types, correspondents)

            self.paperless.update_document(doc_id, metadata)
        except Exception as e:
            self.logger.log_error(f"Error in post-processing document ID {doc_id}: {e}")
            raise

from logger import Logger
from services.document_service import DocumentService
from services.ollama_service import OllamaService
from services.paperless_service import PaperlessService


class PaperlessPostProcessor:
    def __init__(self,
                 logger: Logger,
                 document_service: DocumentService,
                 paperless: PaperlessService,
                 ollama: OllamaService):
        self.logger = logger
        self.document_service = document_service
        self.paperless = paperless
        self.ollama = ollama

    def process_document(self, doc_id):
        try:
            document = self.document_service.get_document(doc_id)
            if not document.text:
                self.logger.log(f"No OCR text found for document ID {doc_id}.")
                return

            metadata = self.ollama.extract_metadata(document.text)
            post_processed_document = self.paperless.post_process(document, metadata)

            self.document_service.update_document(doc_id, post_processed_document)
        except Exception as e:
            self.logger.log_error(f"Error in post-processing document ID {doc_id}: {e}")
            raise

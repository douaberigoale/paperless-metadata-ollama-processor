from logger import Logger
from models.postprocessed_document import PostProcessedDocument
from services.paperless.document_reader import DocumentReader
from services.paperless.document_writer import DocumentWriter


class DocumentService:
    def __init__(self, logger: Logger, api_url, token):
        self.logger = logger
        self.paperless_documents_url = f'{api_url}/documents/'
        self.headers = {'Authorization': f'Token {token}'}
        self.reader = DocumentReader(logger)
        self.writer = DocumentWriter(logger)

    def get_document(self, doc_id):
        return self.reader.get_document(doc_id, self.paperless_documents_url, self.headers)

    def update_document(self, doc_id, post_processed_document: PostProcessedDocument):
        return self.writer.update_document(doc_id, post_processed_document, self.paperless_documents_url, self.headers)

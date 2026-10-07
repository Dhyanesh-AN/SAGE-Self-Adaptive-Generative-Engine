from app.ingestion.loader import PDFDocumentLoader
from app.ingestion.cleaner import TextCleaner
from app.ingestion.splitter import TextSplitter


class IngestionPipeline:

    def __init__(self):

        self.loader = PDFDocumentLoader()
        self.cleaner = TextCleaner()
        self.splitter = TextSplitter()

    def ingest(self, path: str):

        raw_text = self.loader.load(path)

        cleaned_text = self.cleaner.clean(raw_text)

        chunks = self.splitter.split(cleaned_text)

        return chunks
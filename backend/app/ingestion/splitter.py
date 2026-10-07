from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(

            chunk_size=500,

            chunk_overlap=75,

        )

    def split(self, text: str):

        return self.splitter.split_text(text)
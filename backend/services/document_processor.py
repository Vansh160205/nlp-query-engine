import io
from typing import List, Dict
import pypdf
import docx
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# The model is thread-safe and can be loaded once globally to save memory and time
model = SentenceTransformer('all-MiniLM-L6-v2')

class DocumentProcessor:
    """A self-contained class to process and store document data."""
    def __init__(self):
        """
        Initializes instance-specific storage. This is the key fix.
        """
        self.documents_store: Dict[str, Dict] = {}
        embedding_dim = 384  # model output dim
        self.vector_index = faiss.IndexFlatL2(embedding_dim)

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def _extract_text_from_docx(self, file_content: bytes) -> str:
        try:
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""

    def _extract_text_from_txt(self, file_content: bytes) -> str:
        return file_content.decode('utf-8', errors='ignore')

    def _dynamic_chunking(self, content: str) -> List[str]:
        chunks = content.split('\n\n')
        return [c.strip() for c in chunks if c.strip()]

    def process_documents(self, files: List[Dict]) -> Dict:
        """
        Processes documents using the instance's own vector_index and documents_store.
        No more 'global' keyword.
        """
        processed_files = []
        doc_id_counter = len(self.documents_store)

        for file in files:
            filename = file['filename']
            content = file['content']
            ext = filename.split('.')[-1].lower()

            text = ""
            if ext == 'pdf':
                text = self._extract_text_from_pdf(content)
            elif ext == 'docx':
                text = self._extract_text_from_docx(content)
            elif ext == 'txt':
                text = self._extract_text_from_txt(content)
            else:
                continue

            if not text:
                continue

            chunks = self._dynamic_chunking(text)
            if not chunks:
                continue

            embeddings = model.encode(chunks, convert_to_tensor=False)

            for i, chunk in enumerate(chunks):
                doc_id = f"{filename}_{doc_id_counter + i}"
                self.documents_store[doc_id] = {
                    "filename": filename,
                    "chunk": chunk,
                    "embedding_id": self.vector_index.ntotal + i
                }

            self.vector_index.add(np.array(embeddings).astype('float32'))
            processed_files.append(filename)
            doc_id_counter += len(chunks)

        return {
            "status": "success",
            "processed_files": processed_files,
            "total_documents_processed": len(processed_files),
            "total_chunks_indexed": self.vector_index.ntotal
        }


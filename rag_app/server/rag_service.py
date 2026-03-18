import os
import uuid
import requests
import PyPDF2
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.endee_url = os.getenv("ENDEE_URL", "http://localhost:8080")
        self.index_name = "rag_index"
        self.dimension = 384
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        url = f"{self.endee_url}/api/v1/index/create"
        payload = {
            "index_name": self.index_name,
            "dim": self.dimension,
            "space_type": "cosine",
            "precision": "int16"
        }
        try:
            list_url = f"{self.endee_url}/api/v1/index/list"
            resp = requests.get(list_url)
            if resp.status_code == 200:
                indexes = resp.json().get("indexes", [])
                if any(idx["name"] == self.index_name for idx in indexes):
                    return
            resp = requests.post(url, json=payload)
        except Exception as e:
            print(f"Error checking/creating index: {e}")

    def process_pdf(self, file_path: str) -> List[str]:
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF extract error: {e}")

        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        return [c.strip() for c in chunks if c.strip()]

    def ingest_documents(self, chunks: List[str]):
        embeddings = self.encoder.encode(chunks).tolist()
        # Correct URL for vector insertion
        url = f"{self.endee_url}/api/v1/index/{self.index_name}/vector/insert"
        print(f"Ingesting {len(chunks)} chunks to {url}")
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            payload = {
                "id": str(uuid.uuid4())[:8],
                "vector": emb,
                "meta": chunk
            }
            try:
                resp = requests.post(url, json=payload)
                if resp.status_code != 200:
                    print(f"Failed to ingest chunk {i}: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"Ingest error on chunk {i}: {e}")

    def search(self, query: str, k: int = 3) -> List[str]:
        query_emb = self.encoder.encode([query])[0].tolist()
        # Correct URL for search - the username is handled by middleware, so index_name is enough
        url = f"{self.endee_url}/api/v1/index/{self.index_name}/search"
        payload = {"vector": query_emb, "k": k}
        print(f"Searching {url} with k={k}")
        try:
            resp = requests.post(url, json=payload)
            print(f"Search response status: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    import msgpack
                    # Endee ResultSet is packed as [ [result1, result2, ...] ]
                    data = msgpack.unpackb(resp.content)
                    
                    all_results = []
                    # Standard ResultSet packs as [[res1, res2, ...]]
                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], list) and len(data[0]) > 0 and isinstance(data[0][0], list):
                            all_results = data[0]
                        else:
                            all_results = data
                    
                    results = []
                    for res in all_results:
                        if isinstance(res, list) and len(res) >= 3:
                            # res[0]=sim, res[1]=id, res[2]=meta
                            meta = res[2]
                            if isinstance(meta, bytes):
                                results.append(meta.decode('utf-8'))
                            elif isinstance(meta, str):
                                results.append(meta)
                    
                    return results
                except Exception as e:
                    print(f"Decoding error: {e}")
                    # Fallback to JSON if MsgPack fails
                    try:
                        results_raw = resp.json()
                        # JSON usually returns a flat list of objects or [ [obj, ... ] ]
                        # Handle based on what we see in logs if needed
                        return [str(r) for r in results_raw]
                    except:
                        return []
            else:
                print(f"Search failed with status {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"Search error: {e}")
        return []

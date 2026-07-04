import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"
PERMISSIONS_FILE = DATA_DIR / "permissions.json"
DB_FILE = DATA_DIR / "enterprise.db"
SEED_SQL = DATA_DIR / "seed_db.sql"
EVAL_FILE = DATA_DIR / "eval" / "golden_qa.json"
BM25_PICKLE = DATA_DIR / "bm25_index.pkl"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_IN_MEMORY = os.getenv("QDRANT_IN_MEMORY", "true").lower() == "true"
QDRANT_PATH = str(PROJECT_ROOT / "qdrant_data")
COLLECTION_NAME = "enterprise_docs"

MAX_CHUNK_TOKENS = 512
CHUNK_OVERLAP_RATIO = 0.15

CANDIDATES_PER_RETRIEVER = 20
RRF_K = 60
RERANK_TOP_N = 30
FINAL_TOP_K = 5
RETRIEVAL_GATE_THRESHOLD = 0.35

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 1024
LLM_TIMEOUT = 60

SQL_QUERY_TIMEOUT = 5
SQL_ROW_LIMIT = 100

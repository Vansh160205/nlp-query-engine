# backend/services/query_engine.py
import time
import os
from typing import Any, Dict, List, Optional, Tuple
from cachetools import TTLCache
import re
import sqlparse
import numpy as np
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Import your schema discovery & doc processor
from services.schema_discovery import SchemaDiscovery
from services.document_processor import DocumentProcessor, model

# -------------------------
# Globals
# -------------------------
QUERY_HISTORY_LIMIT = 200
_query_history: List[Dict] = []
query_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes TTL

FORBIDDEN_SQL_PATTERNS = [
    r";",
    r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bGRANT\b", r"\bREVOKE\b",
    r"\bEXEC\b", r"\bEXECUTE\b"
]
ALLOWED_STATEMENTS = {"SELECT", "WITH"}

def _normalize_query_key(query: str, schema_hash: str = "") -> str:
    return f"{query.strip().lower()}::schema::{schema_hash}"


class QueryEngine:
    def __init__(self, connection_string: Optional[str] = None):
        self.schema = {}
        self.engine = None
        self.schema_discovery = SchemaDiscovery()
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.doc_processor = DocumentProcessor()
        if connection_string:
            self.connect_db(connection_string)

    def connect_db(self, connection_string: str):
        try:
            self.engine = create_engine(connection_string)
            self.schema = self.schema_discovery.analyze_database(connection_string)
        except Exception as e:
            raise RuntimeError(f"DB connect failed: {e}")

    # -------------------------
    # Query Classification
    # -------------------------
    def classify_query(self, query: str) -> str:
        """
        Classifies a user query as SQL, DOCUMENT, or HYBRID based on keywords
        and matching schema table/column names.
        """
        q_lower = query.lower()
        query_words = set(q_lower.split())

        # --- MODIFICATION START ---
        # Expanded SQL keywords
        sql_keywords = {
            "how many", "count", "average", "avg", "sum", "total", "top", "highest",
            "lowest", "list", "show", "find", "get", "which", "who", "what are", "what is"
        }
        # Document-related keywords
        doc_keywords = {"resume", "cv", "policy", "contract", "review", "document", "pdf"}

        # Dynamically get all table and column names from the schema
        schema_names = set()
        if self.schema and "tables" in self.schema:
            for table in self.schema["tables"]:
                schema_names.add(table["name"].lower())
                for column in table["columns"]:
                    schema_names.add(column["name"].lower())

        # Score based on keyword matches and schema name matches
        sql_score = 0
        for keyword in sql_keywords:
            if keyword in q_lower:
                sql_score += 1
        
        # Check for direct matches with table/column names, which is a strong SQL signal
        for word in query_words:
            # Also check for simple plurals (e.g., 'employees' matches 'employee')
            if word in schema_names or (word.endswith('s') and word[:-1] in schema_names):
                sql_score += 2 # Give higher weight to schema name matches

        doc_score = sum(1 for keyword in doc_keywords if keyword in q_lower)

        # Decision logic
        if sql_score > 0 and doc_score == 0:
            return "SQL"
        if doc_score > 0 and sql_score == 0:
            return "DOCUMENT"
        if sql_score > doc_score:
            return "SQL"
        if doc_score > sql_score:
            return "DOCUMENT"
        
        # If scores are equal or both zero but the query is not empty, default to HYBRID
        return "HYBRID" if query.strip() else "UNKNOWN"


    # -------------------------
    # Helpers
    # -------------------------
    def clean_groq_sql(self,sql: str) -> str:
        """
        Removes Groq markdown code fences like ```sql ... ```
        """
        return re.sub(r"```(?:sql)?\s*|\s*```", "", sql, flags=re.IGNORECASE).strip()

    # -------------------------
    # SQL Safety
    # -------------------------
    def _is_sql_safe(self, sql: str) -> Tuple[bool, str]:
        # Remove backticks and language hints (```sql)
        sql_clean = re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
        
        for pat in FORBIDDEN_SQL_PATTERNS:
            if pat == r";":
                continue  # allow semicolon
            if re.search(pat, sql_clean, flags=re.IGNORECASE):
                return False, f"Forbidden SQL pattern detected: {pat}"

        parsed = sqlparse.parse(sql_clean)
        if not parsed:
            return False, "Unable to parse SQL."

        first_token = parsed[0].token_first(skip_cm=True)
        first_value = getattr(first_token, "value", "").upper() if first_token else ""

        if first_value and first_value.split()[0] not in ALLOWED_STATEMENTS:
            return False, f"Only SELECT/WITH statements allowed. Found: {first_value}"

        return True, "safe"

    def optimize_sql_query(self, sql: str, default_limit: int = 200) -> str:
        lower = sql.lower()
        if "limit" not in lower:
            sql = f"{sql.rstrip().rstrip(';')} LIMIT {default_limit}"
        return sql

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        if self.engine is None:
            return {"error": "No DB engine connected."}

        safe, msg = self._is_sql_safe(sql)
        if not safe:
            return {"error": f"SQL safety check failed: {msg}"}

        sql = self.optimize_sql_query(sql)
        try:
            start = time.time()
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = [dict(r._mapping) for r in result.fetchall()]
            elapsed = time.time() - start
            return {"rows": rows, "elapsed_seconds": elapsed}
        except SQLAlchemyError as e:
            return {"error": f"SQL execution error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected SQL execution error: {e}"}

    # -------------------------
    # LLM-based SQL Generation
    # -------------------------
    def generate_sql_with_groq(self, user_query: str) -> Optional[str]:
        if not self.schema or "tables" not in self.schema:
            print("Current schema:", self.schema)
            return None

        schema_text = "\n".join(
            [f"Table {t['name']}({', '.join([c['name'] for c in t['columns']])})"
             for t in self.schema["tables"]]
        )

        prompt = f"""
        You are a helpful assistant that converts natural language into SQL.
        Given the following schema:

        {schema_text}

        User query: "{user_query}"

        Output ONLY a SQL query. Do not include explanations.
        """

        try:
            resp = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            print(f"GROQ response: {resp}")
            sql = resp.choices[0].message.content.strip()
            return sql
        except Exception as e:
            print(f"GROQ SQL generation error: {e}")
            return None

    # -------------------------
    # Document Search
    # -------------------------
    def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        # This now correctly uses the instance-specific processor
        if self.doc_processor.vector_index is None or self.doc_processor.vector_index.ntotal == 0:
            return {"results": [], "elapsed_seconds": 0.0, "note": "No indexed documents."}

        start = time.time()
        q_vec = model.encode([query], convert_to_tensor=False)
        q_vec = np.array(q_vec).astype("float32")
        
        distances, indices = self.doc_processor.vector_index.search(q_vec, top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
             if idx == -1: continue
             for doc_id, meta in self.doc_processor.documents_store.items():
                 if meta.get("embedding_id") == int(idx):
                    results.append({
                        "doc_id": doc_id,
                        "filename": meta.get("filename"),
                        "chunk": meta.get("chunk"),
                        "distance": float(dist)
                    })
                    break
        
        elapsed = time.time() - start
        return {"results": results, "elapsed_seconds": elapsed}

    # -------------------------
    # Process Query
    # -------------------------
    def process_query(self, user_query: str, top_k_docs: int = 5, schema_hash: str = "") -> Dict[str, Any]:
        key = _normalize_query_key(user_query, schema_hash)

        if key in query_cache:
            cached_resp = query_cache[key]
            cached_resp["_cache_hit"] = True
            _query_history.insert(0, {"query": user_query, "cached": True, "time": time.time()})
            _query_history[:] = _query_history[:QUERY_HISTORY_LIMIT]
            return cached_resp

        qtype = self.classify_query(user_query)
        response = {
            "query": user_query,
            "query_type": qtype,
            "sql": None,
            "sql_result": None,
            "document_result": None,
            "metrics": {},
            "error": None
        }

        try:
            if qtype in ("SQL", "HYBRID"):
                generated_sql = None
                if re.match(r"^\s*(select|with)\b", user_query.strip(), flags=re.I):
                    generated_sql = user_query.strip()
                else:
                    generated_sql = self.generate_sql_with_groq(user_query)

                if generated_sql:
                    generated_sql_clean = self.clean_groq_sql(generated_sql)
                    response["sql"] = generated_sql_clean
                    response["sql_result"] = self.execute_sql(generated_sql_clean)
                else:
                    response["sql_result"] = {"error": "Could not generate SQL with Groq."}

            if qtype in ("DOCUMENT", "HYBRID"):
                response["document_result"] = self.search_documents(user_query, top_k=top_k_docs)

            response["metrics"]["timestamp"] = time.time()
            response["_cache_hit"] = False

            query_cache[key] = response
            _query_history.insert(0, {"query": user_query, "cached": False, "time": time.time(), "type": qtype})
            _query_history[:] = _query_history[:QUERY_HISTORY_LIMIT]

            return response
        except Exception as e:
            return {"error": f"Processing failed: {e}"}

    # -------------------------
    # Query History
    # -------------------------
    def get_history(self, limit: int = 50) -> List[Dict]:
        return _query_history[:limit]

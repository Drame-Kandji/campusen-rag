"""
PHASE 7a : RETRIEVAL (v3 — multi-établissements)
----------------------------------------------------
Si la question mentionne PLUSIEURS établissements (ou une ville regroupant
plusieurs établissements), on interroge CHAQUE établissement séparément
et on fusionne les résultats. Sans ça, la recherche vectorielle globale
favorise souvent un seul établissement (celui dont le contenu "ressemble"
le plus au vecteur de la question) et les autres disparaissent — c'est
exactement ce qui faisait échouer "UCAD vs UGB".
"""

from src.embeddings.embedder import embed_text
from src.vectordb.vector_store import VectorStore
from src.retrieval.known_institutions import detect_institutions


class Retriever:
    def __init__(self, vector_store: VectorStore, embedding_model: str = "nomic-embed-text", top_k: int = 6):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.top_k = top_k

    def retrieve(self, question: str) -> list[dict]:
        question_vector = embed_text(question, model=self.embedding_model)
        institutions = detect_institutions(question)

        if not institutions:
            # Aucun établissement détecté : recherche globale classique
            return self.vector_store.query(question_vector, top_k=self.top_k)

        print(f"[retrieval] Établissement(s) détecté(s) : {institutions}")

        # Un établissement à la fois, avec sa propre part du top_k,
        # pour garantir que chacun soit représenté dans le résultat final
        per_institution_k = max(2, self.top_k // len(institutions))
        merged = []
        seen_ids = set()

        for institution in institutions:
            matches = self.vector_store.query(
                question_vector, top_k=per_institution_k, etablissement=institution
            )
            for m in matches:
                key = m["text"][:50]  # évite les doublons si un chunk ressort deux fois
                if key not in seen_ids:
                    seen_ids.add(key)
                    merged.append(m)

        if not merged:
            print("[retrieval] Aucun résultat filtré, recherche élargie")
            merged = self.vector_store.query(question_vector, top_k=self.top_k)

        return merged
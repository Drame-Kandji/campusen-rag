"""
PHASE 6 : BASE VECTORIELLE (ChromaDB)
----------------------------------------
Rôle : stocker les vecteurs d'embeddings + le texte associé, de façon
persistante sur le disque, et permettre une recherche par similarité.

On encapsule ça dans une classe car on a un état à garder : la connexion
au client et à la collection, créée une seule fois puis réutilisée.
"""

import chromadb


class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "campusen_rag"):
        # PersistentClient = les données sont écrites sur le disque,
        # donc elles survivent entre deux exécutions du script.
        self.client = chromadb.PersistentClient(path=persist_directory)

        # get_or_create : si la collection existe déjà (ingestion précédente),
        # on la réutilise. Sinon on la crée.
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]):
        """Ajoute des chunks et leurs vecteurs, avec toutes leurs métadonnées."""
        self.collection.add(
            ids=[c["chunk_id"] for c in chunks],
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=[
                {
                    "source": c["source"],
                    "url": c.get("url") or "",
                    "etablissement": c.get("etablissement") or "",
                }
                for c in chunks
            ],
        )
        print(f"[vectordb] {len(chunks)} chunks ajoutés à la collection.")

    def query(self, query_embedding: list[float], top_k: int = 4, etablissement: str | None = None) -> list[dict]:
        """
        Recherche les top_k chunks les plus proches.

        Si etablissement est fourni, la recherche est restreinte aux chunks
        de cet établissement uniquement (filtrage par métadonnées, avant même
        le calcul de similarité) — beaucoup plus précis qu'une recherche
        vectorielle "à l'aveugle" sur toute la base.
        """
        where_clause = {"etablissement": etablissement} if etablissement else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
        )

        matches = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i]
            matches.append({
                "text": results["documents"][0][i],
                "source": meta["source"],
                "url": meta.get("url") or None,
                "etablissement": meta.get("etablissement") or None,
                "distance": results["distances"][0][i],
            })
        return matches
      
    def count(self) -> int:
        """Nombre de chunks actuellement stockés dans la collection."""
        return self.collection.count()
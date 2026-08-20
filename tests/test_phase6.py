"""
Script de test — PHASE 6 : ingestion complète jusqu'au stockage.

But : enchaîner Phase 3 (lecture) -> Phase 4 (chunking) -> Phase 5 (embeddings)
-> Phase 6 (stockage), et vérifier que tout est bien dans ChromaDB.

Lancement : python3 test_phase6.py
Attention : ça peut prendre 10-30 secondes (20 chunks à vectoriser sur CPU).
"""

from src.ingestion.loader import load_documents
from src.chunking.chunker import chunk_documents
from src.embeddings.embedder import embed_batch
from src.vectordb.vector_store import VectorStore

# Phase 3 : lecture
documents = load_documents("data/raw")

# Phase 4 : chunking
chunks = chunk_documents(documents, chunk_size=300, chunk_overlap=50)

# Phase 5 : embeddings
print(f"\nGénération de {len(chunks)} vecteurs...")
texts = [c["text"] for c in chunks]
embeddings = embed_batch(texts)

# Phase 6 : stockage
store = VectorStore(persist_directory="./chroma_db", collection_name="campusen_rag")
store.add_chunks(chunks, embeddings)

print(f"\nTotal dans la base : {store.count()} chunks stockés.")

# Petit test de recherche pour vérifier que ça marche
from src.embeddings.embedder import embed_text
question_vector = embed_text("conditions d'accès à la licence informatique")
resultats = store.query(question_vector, top_k=3)

print("\n--- Test de recherche : 'conditions d'accès à la licence informatique' ---")
for r in resultats:
    print(f"\nSource   : {r['source']}")
    print(f"Distance : {r['distance']:.4f}")
    print(f"Texte    : {r['text'][:150]}...")
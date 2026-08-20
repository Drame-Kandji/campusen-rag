"""
Script de test — PHASE 4 uniquement.

But : vérifier que le chunking fonctionne bien sur nos 3 documents de test,
avant de passer aux embeddings (Phase 5).

Lancement : python3 test_phase4.py
"""

from src.ingestion.loader import load_documents
from src.chunking.chunker import chunk_documents

documents = load_documents("data/raw")
chunks = chunk_documents(documents, chunk_size=300, chunk_overlap=50)

print(f"\n--- {len(chunks)} chunk(s) au total ---")
for chunk in chunks[:3]:  # on affiche juste les 3 premiers pour vérifier
    print(f"\nchunk_id : {chunk['chunk_id']}")
    print(f"source   : {chunk['source']}")
    print(f"texte    : {chunk['text'][:100]}...")
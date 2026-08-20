"""
Script de test — PHASE 7 : le RAG complet, du bout en bout.

But : poser une vraie question et obtenir une vraie réponse générée par
mistral, basée sur nos documents de test.

Prérequis : avoir déjà lancé test_phase6.py au moins une fois (la base
ChromaDB doit déjà contenir les chunks).

Lancement : python3 test_phase7.py
"""

from src.vectordb.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.llm.llm_client import generate_answer

store = VectorStore(persist_directory="./chroma_db", collection_name="campusen_rag")
print(f"Chunks disponibles dans la base : {store.count()}")

retriever = Retriever(vector_store=store, top_k=3)

question = "J'ai un bac S2, je veux faire de l'informatique, quelles sont mes options ?"

print(f"\n❓ Question : {question}")

chunks = retriever.retrieve(question)
print(f"\n[retrieval] {len(chunks)} chunks trouvés :")
for c in chunks:
    print(f"  - {c['source']} (distance: {c['distance']:.2f})")

print("\n[llm] Génération de la réponse avec mistral...\n")
answer = generate_answer(question, chunks, model="mistral")

print(f"💬 Réponse :\n{answer}")






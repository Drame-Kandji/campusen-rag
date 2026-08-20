"""
Script de test — PHASE 3 uniquement.

But : vérifier que loader.py lit bien nos documents de test, avant de passer
à la suite du pipeline. Pas encore le programme final (ça viendra en Phase 7
avec main.py).

Lancement : python3 test_phase3.py
"""

from src.ingestion.loader import load_documents

documents = load_documents("data/raw")

print(f"\n--- {len(documents)} document(s) chargé(s) ---")
for doc in documents:
    apercu = doc["text"][:150].replace("\n", " ")
    print(f"\nSource : {doc['source']}")
    print(f"Aperçu : {apercu}...")

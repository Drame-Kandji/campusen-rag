"""
Script de test — PHASE 5 uniquement.

But : vérifier que nomic-embed-text fonctionne bien via Ollama, et voir
concrètement à quoi ressemble un vecteur d'embedding.

Lancement : python3 test_phase5.py
"""

from src.embeddings.embedder import embed_text

texte_exemple = "Quelles sont les conditions d'accès à la licence informatique ?"

print(f"Texte : {texte_exemple}\n")
print("Génération du vecteur en cours...")

vecteur = embed_text(texte_exemple)

print(f"\nDimension du vecteur : {len(vecteur)}")
print(f"Premiers 5 nombres    : {vecteur[:5]}")
print(f"Type de chaque valeur : {type(vecteur[0])}")
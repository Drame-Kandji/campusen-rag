"""
PHASE 5 : EMBEDDINGS
----------------------
Rôle : transformer un texte en vecteur numérique (liste de floats) qui
capture son sens. On utilise le modèle nomic-embed-text via Ollama —
100% local, gratuit, déjà téléchargé en Phase 1.

Rappel important : c'est un modèle DIFFÉRENT de mistral/llama3.2.
mistral/llama3.2 génèrent du texte. nomic-embed-text génère des vecteurs.
Ce sont deux tâches différentes, faites par deux modèles différents.
"""

import ollama


def embed_text(text: str, model: str = "nomic-embed-text") -> list[float]:
    """
    Transforme UN texte en UN vecteur d'embedding.

    ollama.embeddings() envoie le texte au modèle et reçoit en retour
    un dict contenant la clé "embedding" (la liste de nombres).
    """
    response = ollama.embeddings(model=model, prompt=text)
    return response["embedding"]


def embed_batch(texts: list[str], model: str = "nomic-embed-text") -> list[list[float]]:
    """
    Transforme une LISTE de textes en liste de vecteurs, un par un.

    On affiche une progression tous les 5 chunks car sur CPU, générer
    des embeddings peut prendre quelques secondes par chunk.
    """
    vectors = []
    for i, text in enumerate(texts):
        vectors.append(embed_text(text, model))
        if (i + 1) % 5 == 0 or (i + 1) == len(texts):
            print(f"[embeddings] {i + 1}/{len(texts)} chunks vectorisés")
    return vectors
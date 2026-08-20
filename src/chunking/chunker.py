"""
PHASE 4 : CHUNKING
--------------------
Rôle : découper un texte long en petits morceaux (chunks) de taille fixe,
avec un léger chevauchement entre eux pour ne pas couper une idée en deux.

Pourquoi c'est nécessaire :
- Un LLM et un modèle d'embedding ont une fenêtre de contexte limitée.
- Un chunk trop grand dilue la pertinence de la recherche (le vecteur
  devient une moyenne floue de plusieurs sujets).
- Un chunk trop petit perd le contexte (une phrase coupée ne veut rien dire).

On utilise un découpage par fenêtre glissante (sliding window) :
on avance de (chunk_size - chunk_overlap) caractères à chaque itération.
"""


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Découpe un texte en chunks avec chevauchement."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap doit être plus petit que chunk_size")

    chunks = []
    start = 0
    text_length = len(text)
    step = chunk_size - chunk_overlap  # de combien on avance à chaque tour

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:  # on ignore les chunks vides (fin de texte)
            chunks.append(chunk)
        start += step

    return chunks


def chunk_documents(documents: list[dict], chunk_size: int = 600, chunk_overlap: int = 80) -> list[dict]:
    """
    Applique chunk_text() à une liste de documents.

    Point clé : chaque chunk hérite des métadonnées (url, établissement)
    du document entier — pas seulement le premier chunk. C'est ce qui
    permet au LLM de toujours savoir de quel établissement parle un extrait,
    peu importe où il se trouve dans le document original.
    """
    all_chunks = []
    for doc in documents:
        pieces = chunk_text(doc["text"], chunk_size, chunk_overlap)
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": f"{doc['source']}_{i}",
                "text": piece,
                "url": doc.get("url"),
                "etablissement": doc.get("etablissement"),
            })
        print(f"[chunking] {doc['source']} -> {len(pieces)} chunks")

    return all_chunks
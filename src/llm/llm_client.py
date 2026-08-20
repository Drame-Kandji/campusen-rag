"""
PHASE 7b : GÉNÉRATION (LLM)
------------------------------
Rôle : construire le prompt final (question + contexte récupéré) et l'envoyer
à mistral/llama3.2 via Ollama pour générer la réponse.

C'est ici que se joue la fiabilité du RAG : le prompt système force le
modèle à s'appuyer STRICTEMENT sur le contexte fourni, et à dire "je ne
sais pas" si l'information n'y est pas. Sans ça, le modèle peut halluciner
en inventant des infos à partir de ses connaissances générales.
"""

import ollama
import os
from groq import Groq

SYSTEM_PROMPT = """Tu es un assistant qui aide les nouveaux bacheliers sénégalais
à comprendre Campusen et à s'orienter vers une formation, en te basant
UNIQUEMENT sur le contexte fourni ci-dessous.

Règles de contenu :
- Chaque extrait de contexte est étiqueté avec son établissement d'origine.
  NE MÉLANGE JAMAIS les informations de deux établissements différents.
- N'invente JAMAIS le nom d'un établissement, d'un département ou d'une
  formation. Utilise UNIQUEMENT les noms exacts tels qu'ils apparaissent
  dans le contexte. Si un nom te semble tronqué ou peu clair, ne le
  présente pas comme un fait séparé.
- Si la question porte sur un établissement précis et qu'aucun extrait
  étiqueté avec cet établissement ne répond à la question, dis clairement
  que tu ne sais pas plutôt que d'utiliser un extrait d'un autre établissement.
- Réponds en français, de façon claire et directe.

Règles de format (important) :
- Réponds comme dans une conversation, pas comme un rapport. Des phrases
  courtes, un ton naturel.
- N'utilise JAMAIS de tableaux markdown.
- N'utilise PAS de titres (#, ##...) ni de citations en bloc (>).
- Pour lister plusieurs formations, utilise simplement des tirets "-",
  un par ligne, avec le nom en gras et une courte explication après.
- Reste concis : 3 à 6 phrases pour une réponse simple, un peu plus
  seulement si la question demande explicitement une liste longue.
"""


def build_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    """Construit le prompt, avec un label établissement explicite par chunk."""
    context_blocks = []
    for chunk in retrieved_chunks:
        label = chunk.get("etablissement") or chunk["source"]
        context_blocks.append(f"[Établissement : {label}]\n{chunk['text']}")

    context = "\n\n---\n\n".join(context_blocks)

    return f"""Contexte :
{context}

Question : {question}

Réponse :"""


def generate_answer(question: str, retrieved_chunks: list[dict], model: str = "mistral") -> str:
    """Version non-streaming (gardée pour les tests en script, test_phase7.py)."""
    prompt = build_prompt(question, retrieved_chunks)

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        keep_alive="30m",  # garde le modèle en RAM 30 min après chaque appel,
                            # évite de le recharger à chaque question
    )

    return response["message"]["content"]


def generate_answer_stream(question: str, retrieved_chunks: list[dict], model: str = "mistral"):
    """
    Version streaming : au lieu de retourner le texte complet d'un coup,
    cette fonction est un générateur Python (mot-clé `yield`) qui renvoie
    chaque morceau de réponse dès qu'Ollama le produit.

    stream=True demande à Ollama d'envoyer la réponse progressivement,
    au lieu d'attendre la fin de la génération complète.
    """
    prompt = build_prompt(question, retrieved_chunks)

    stream = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        keep_alive="30m",
    )

    for chunk in stream:
        piece = chunk["message"]["content"]
        if piece:
            yield piece
            
            

def generate_answer_stream_groq(question: str, retrieved_chunks: list[dict], model: str = "openai/gpt-oss-20b"):
    """
    Version streaming utilisant Groq (modèle hébergé, beaucoup plus rapide
    que l'inférence locale sur CPU). Nécessite GROQ_API_KEY dans .env.
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompt = build_prompt(question, retrieved_chunks)

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece
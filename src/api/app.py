"""
PHASE 8 : API BACKEND
------------------------
Rôle : exposer notre RAG via une route HTTP, pour qu'une interface web
(Phase 9) ou n'importe quel client puisse l'utiliser.

On charge le VectorStore et le Retriever UNE SEULE FOIS au démarrage du
serveur (au niveau du module, pas dans la fonction ask) — sinon on
recréerait la connexion ChromaDB à chaque requête, ce qui serait lent.

Lancement :
    uvicorn src.api.app:app --reload

Puis test :
    curl -X POST http://127.0.0.1:8000/ask \
         -H "Content-Type: application/json" \
         -d '{"question": "Quel bac pour faire informatique ?"}'
"""

from fastapi import FastAPI
from pydantic import BaseModel

from src.vectordb.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.llm.llm_client import generate_answer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from src.llm.llm_client import generate_answer_stream
from dotenv import load_dotenv
load_dotenv()
from src.llm.llm_client import generate_answer_stream_groq

app = FastAPI(title="Campusen RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en développement uniquement — à restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_source_label(raw_source: str) -> str:
    """
    Filet de sécurité : si un chunk n'a pas d'établissement identifié
    (fichier ajouté sans en-tête de métadonnées), on affiche au moins
    un nom lisible plutôt que le nom de fichier technique brut.
    """
    name = raw_source.rsplit(".", 1)[0]  # retire l'extension (.txt, .pdf)
    name = name.replace("_", " ").replace("-", " ")
    return name.strip().title()

# Chargé une seule fois au démarrage du serveur
store = VectorStore(persist_directory="./chroma_db", collection_name="campusen_rag")
retriever = Retriever(vector_store=store, top_k=5)


class Question(BaseModel):
    """
    Pydantic valide automatiquement que le JSON reçu contient bien
    un champ "question" de type texte. Si ce n'est pas le cas,
    FastAPI renvoie une erreur claire sans qu'on ait à la coder nous-mêmes.
    """
    question: str


@app.get("/")
def health_check():
    """Route simple pour vérifier que le serveur tourne et voir combien de chunks sont indexés."""
    return {"status": "ok", "chunks_in_db": store.count()}


@app.post("/ask")
def ask(payload: Question):
    """
    Route principale : reçoit une question, fait le retrieval + la génération,
    renvoie la réponse ET les sources utilisées (transparence pour l'utilisateur).
    """
    chunks = retriever.retrieve(payload.question)
    answer = generate_answer(payload.question, chunks, model="mistral")
    
    #answer = generate_answer(payload.question, chunks, model="llama3.2")

    return {
        "question": payload.question,
        "answer": answer,
        "sources": [c["source"] for c in chunks],
    }
    
@app.post("/ask-stream")
def ask_stream(payload: Question):
    """
    Version streaming de /ask. Récupère les chunks pertinents une seule fois,
    puis renvoie la réponse du LLM au fur et à mesure qu'elle est générée.
    """
    chunks = retriever.retrieve(payload.question)

    # On déduplique par URL (ou par nom de fichier si pas d'URL)
    seen = set()
    sources = []
    for c in chunks:
        key = c["url"] or c["source"]
        if key not in seen:
            seen.add(key)
            label = c.get("etablissement") or clean_source_label(c["source"])
            sources.append({"label": label, "url": c["url"]})
            
    def event_generator():
        import json
        yield f"SOURCES:{json.dumps(sources)}\n"
        #for piece in generate_answer_stream(payload.question, chunks, model="mistral"):
        for piece in generate_answer_stream_groq(payload.question, chunks):
            yield piece

    return StreamingResponse(event_generator(), media_type="text/plain")

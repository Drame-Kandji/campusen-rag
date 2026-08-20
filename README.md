# Campusen RAG: Assistant d'orientation pour bacheliers

Assistant conversationnel basé sur un RAG (Retrieval-Augmented Generation), construit
étape par étape pour comprendre chaque brique, pas juste copier du code.

## Suivi d'avancement

- [x] Phase 0 — Comprendre les concepts (LLM, RAG, embedding, chunk, retrieval)
- [x] Phase 1 — Structure du projet + installation
- [x] Phase 2 — Données de test créées (data/raw/) — à remplacer par les vraies données Campusen
- [x] Phase 3 — Nettoyer les documents
- [x] Phase 4 — Chunking
- [x] Phase 5 — Embeddings
- [x] Phase 6 — Base vectorielle
- [x] Phase 7 — Assembler le RAG (retrieval + prompt + LLM)
- [x] Phase 8 — API backend
- [x] Phase 9 — Interface web
- [x] Phase 10 — Tests

## Stack

- **LLM génération** : Ollama (`mistral` ou `llama3.2`, déjà installés)
- **Embeddings** : Ollama (`nomic-embed-text`, à installer)
- **Base vectorielle** : ChromaDB (locale, persistante)
- **Backend** : Python (API à ajouter en phase 8)

## Installation (Phase 1)

```bash
cd campusen-rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# modèle d'embedding (différent de mistral/llama3.2 qui servent à générer du texte)
ollama pull nomic-embed-text
```

Vérifie que tout fonctionne :

```bash
ollama list          # doit afficher mistral, llama3.2, ET nomic-embed-text
python3 -c "import chromadb, pypdf, yaml, ollama; print('OK')"
```

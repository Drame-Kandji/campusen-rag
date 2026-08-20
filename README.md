# Campusen RAG — Assistant d'orientation pour bacheliers

Assistant conversationnel basé sur un RAG (Retrieval-Augmented Generation), construit
étape par étape pour comprendre chaque brique, pas juste copier du code.

## Suivi d'avancement

- [x] Phase 0 — Comprendre les concepts (LLM, RAG, embedding, chunk, retrieval)
- [x] Phase 1 — Structure du projet + installation
- [x] Phase 2 — Données de test créées (data/raw/) — à remplacer par les vraies données Campusen
- [ ] Phase 3 — Nettoyer les documents
- [ ] Phase 4 — Chunking
- [ ] Phase 5 — Embeddings
- [ ] Phase 6 — Base vectorielle
- [ ] Phase 7 — Assembler le RAG (retrieval + prompt + LLM)
- [ ] Phase 8 — API backend
- [ ] Phase 9 — Interface web
- [ ] Phase 10 — Tests

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

## Structure actuelle

```
campusen-rag/
├── README.md
├── requirements.txt
├── .gitignore
├── data/raw/
│   ├── campusen_fonctionnement.txt      (test — fonctionnement de la plateforme)
│   ├── formations_ucad_informatique.txt (test — exemple filières UCAD)
│   └── formations_isep_exemple.txt      (test — exemple filières ISEP)
└── src/            ← vide pour l'instant, rempli phase par phase
```

⚠️ Les fichiers dans `data/raw/` sont des données de TEST simplifiées, pour
valider le pipeline technique. Une fois le RAG fonctionnel, il faudra les
remplacer par les vraies données officielles (Campusen, universités, ISEP,
écoles).

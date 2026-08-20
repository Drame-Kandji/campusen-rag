"""
PHASE 3 : LECTURE DES DOCUMENTS
--------------------------------
Rôle : transformer les fichiers bruts de data/raw/ (texte sur le disque)
en texte exploitable par Python (chaînes de caractères en mémoire).

On garde toujours le nom du fichier source à côté du texte : ça nous servira
plus tard pour dire à l'utilisateur "cette réponse vient de tel document".
"""

from pathlib import Path
from pypdf import PdfReader


def load_txt(file_path: Path) -> str:
    """Lit un fichier .txt et retourne son contenu en texte brut."""
    return file_path.read_text(encoding="utf-8", errors="ignore")


def load_pdf(file_path: Path) -> str:
    """
    Lit un fichier .pdf et retourne son contenu en texte brut.

    Un PDF est composé de pages ; pypdf sait extraire le texte de chaque page.
    On les recolle avec un saut de ligne entre chaque page.
    """
    reader = PdfReader(str(file_path))
    pages_text = []
    for page in reader.pages:
        content = page.extract_text() or ""  # extract_text() peut retourner None
        pages_text.append(content)
    return "\n".join(pages_text)


def load_documents(raw_dir: str = "data/raw") -> list[dict]:
    """
    Parcourt data/raw/ et charge tous les fichiers .txt et .pdf.

    Pour les fichiers scrapés (qui commencent par un en-tête
    "SOURCE URL : ...\nÉTABLISSEMENT : ...\nCATÉGORIE : ..."), on extrait
    ces métadonnées UNE FOIS, ici, et on les retire du texte avant chunking.
    Elles seront réappliquées à CHAQUE chunk plus tard (chunker.py) — c'est
    ça qui corrige le problème "seul le premier chunk connaît la source".

    Retourne une liste de dicts :
        {"source": nom_fichier, "text": contenu_sans_entete,
         "url": url_ou_None, "etablissement": nom_ou_None}
    """
    raw_path = Path(raw_dir)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Le dossier {raw_dir} n'existe pas. Vérifie que tu lances "
            f"le script depuis la racine du projet campusen-rag/."
        )

    documents = []

    for file_path in sorted(raw_path.iterdir()):
        extension = file_path.suffix.lower()

        if extension == ".txt":
            text = load_txt(file_path)
        elif extension == ".pdf":
            text = load_pdf(file_path)
        else:
            continue

        if not text.strip():
            continue

        # Extraction de l'en-tête s'il existe (fichiers scrapés uniquement)
        url = None
        etablissement = None
        lines = text.split("\n")
        body_start = 0

        for i, line in enumerate(lines[:5]):  # l'en-tête est toujours dans les 5 premières lignes
            if line.startswith("SOURCE URL : "):
                url = line.replace("SOURCE URL : ", "").strip()
                body_start = i + 1
            elif line.startswith("ÉTABLISSEMENT : "):
                etablissement = line.replace("ÉTABLISSEMENT : ", "").strip()
                body_start = i + 1
            elif line.startswith("CATÉGORIE : "):
                body_start = i + 1

        clean_text = "\n".join(lines[body_start:]).strip()

        documents.append({
            "source": file_path.name,
            "text": clean_text,
            "url": url,
            "etablissement": etablissement,
        })
        print(f"[ingestion] Chargé : {file_path.name} ({len(clean_text)} caractères)"
              + (f" — {etablissement}" if etablissement else ""))

    if not documents:
        print(f"[ingestion] Aucun document trouvé dans {raw_dir}/.")

    return documents
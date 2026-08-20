"""
PHASE 2bis : SCRAPING (v2 — CSV + support PDF)
--------------------------------------------------
Rôle : lire data/sources.csv, et pour chaque ligne :
- si c'est une page web : extraire le texte principal avec trafilatura
- si c'est un PDF : le télécharger tel quel (notre loader.py sait déjà le lire)

On garde la catégorie et l'établissement dans le nom de fichier, ça nous
permettra plus tard de filtrer les réponses par type de source si besoin.
"""

import time
import csv
import requests
import trafilatura
from pathlib import Path
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CampusenRAG-Bot/1.0; projet étudiant EPT)"
}


def slugify(text: str) -> str:
    """Transforme un texte en nom de fichier sûr (pas d'espaces/accents)."""
    import re, unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return text


def fetch_web_page(url: str, max_chars: int = 30000) -> str | None:
    """
    Télécharge une page et en extrait le texte principal (mode lecture).

    max_chars : limite de sécurité. Certains sites (flux d'actualités infinis)
    font extraire à trafilatura des dizaines de milliers de caractères de
    bruit au lieu du contenu ciblé — on tronque pour éviter qu'une seule
    source ne pollue toute la base avec du contenu peu pertinent.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[scraping] Erreur pour {url} : {e}")
        return None

    text = trafilatura.extract(response.text, include_tables=True)
    if not text or len(text.strip()) < 100:
        print(f"[scraping] Contenu insuffisant pour {url}")
        return None

    if len(text) > max_chars:
        print(f"[scraping] ⚠️  Contenu anormalement long ({len(text)} car.) pour {url} — tronqué à {max_chars}")
        text = text[:max_chars]

    return text


def fetch_pdf(url: str, output_path: Path) -> bool:
    """Télécharge un PDF tel quel (pas d'extraction ici, loader.py s'en charge à l'ingestion)."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[scraping] Erreur pour {url} : {e}")
        return False

    output_path.write_bytes(response.content)
    return True


def scrape_from_csv(csv_path: str = "data/sources.csv", output_dir: str = "data/raw", delay: float = 2.0):
    """Lit data/sources.csv et scrape chaque source selon son type (web ou pdf)."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"{len(rows)} sources à traiter.\n")

    for i, row in enumerate(rows):
        url = row["url"].strip()
        source_type = row["type"].strip().lower()
        categorie = slugify(row["categorie"])
        etablissement = slugify(row["etablissement"])

        print(f"({i+1}/{len(rows)}) [{row['type']}] {row['etablissement']} — {url}")

        domain = urlparse(url).netloc.replace(".", "_")
        path_slug = slugify(urlparse(url).path) or "accueil"
        base_name = f"{categorie}_{etablissement}_{domain}_{path_slug}"

        if source_type == "pdf":
            filepath = output_path / f"{base_name}.pdf"
            success = fetch_pdf(url, filepath)
            if success:
                print(f"  -> PDF sauvegardé : {filepath.name}")
        else:
            text = fetch_web_page(url)
            if text:
                filepath = output_path / f"{base_name}.txt"
                content = f"SOURCE URL : {url}\nÉTABLISSEMENT : {row['etablissement']}\nCATÉGORIE : {row['categorie']}\n\n{text}"
                filepath.write_text(content, encoding="utf-8")
                print(f"  -> sauvegardé : {filepath.name} ({len(text)} caractères)")

        if i < len(rows) - 1:
            time.sleep(delay)

    print("\n✅ Scraping terminé.")
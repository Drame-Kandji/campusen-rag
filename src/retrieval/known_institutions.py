"""
Détection d'établissements ET de villes dans une question, pour orienter
le retrieval vers les bonnes sources.

Deux évolutions par rapport à la version précédente :
1. detect_institutions() (au pluriel) renvoie une LISTE, pas un seul nom —
   nécessaire pour les questions de comparaison ("UCAD vs UGB").
2. Une question qui mentionne une VILLE ("Thiès") est maintenant reliée
   à tous les établissements de cette ville, même si leur nom exact
   n'apparaît pas dans la question.
"""

KNOWN_INSTITUTIONS = [
    "Campusen", "MESRI", "Office du Bac",
    "UIDT", "UCAD", "UGB", "UASZ", "UADB", "USSEIN", "UN-CHK",
    "ISEP Thiès", "ISEP Diamniadio", "ISEP Mbacké",
    "ISEP Richard-Toll", "ISEP Bignona", "ISEP Matam",
]

# Ville -> établissements qui s'y trouvent. Permet de répondre correctement
# à "quelles formations à Thiès ?" sans que "Thiès" soit un nom d'établissement.
CITY_TO_INSTITUTIONS = {
    "thies": ["UIDT", "ISEP Thiès"],
    "dakar": ["UCAD"],
    "saint louis": ["UGB"],
    "ziguinchor": ["UASZ"],
    "bambey": ["UADB"],
    "kaolack": ["USSEIN"],
    "diamniadio": ["ISEP Diamniadio"],
    "mbacke": ["ISEP Mbacké"],
    "richard toll": ["ISEP Richard-Toll"],
    "bignona": ["ISEP Bignona"],
    "matam": ["ISEP Matam"],
}


def normalize(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text.lower()


def _all_words_present(name: str, normalized_question: str) -> bool:
    stopwords = {"de", "du", "des", "la", "le", "l"}
    words = [w for w in normalize(name).split() if w not in stopwords]
    return all(word in normalized_question for word in words)


def detect_institutions(question: str) -> list[str]:
    """
    Renvoie TOUS les établissements pertinents pour la question :
    - ceux nommés explicitement (ex: "UCAD", "ISEP de Thiès")
    - ceux déduits d'une ville mentionnée (ex: "Thiès" -> UIDT + ISEP Thiès)

    Pas de doublons dans le résultat.
    """
    normalized_question = normalize(question)
    found = []

    for institution in KNOWN_INSTITUTIONS:
        if _all_words_present(institution, normalized_question):
            found.append(institution)

    for city, institutions in CITY_TO_INSTITUTIONS.items():
        if _all_words_present(city, normalized_question):
            for inst in institutions:
                if inst not in found:
                    found.append(inst)

    return found
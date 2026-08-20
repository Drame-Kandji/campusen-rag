"""
Script de lancement du scraping — lit data/sources.csv

Lancement : python3 scrape.py
"""

from src.scraping.scraper import scrape_from_csv

scrape_from_csv("data/sources.csv")
from bs4 import BeautifulSoup
import sys

with open("jio_plans_7746815442.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")
    
# Jio categories are typically inside buttons or spans in a scrollable header
categories = soup.find_all(text=True)
cats = set()
for text in categories:
    text = text.strip()
    if 3 < len(text) < 30 and "\n" not in text:
        cats.add(text)

print(sorted(list(cats)))

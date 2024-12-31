# Convertisseur PDF vers Image et JSON

Ce script Python permet de :
1. Convertir un fichier PDF en images
2. Extraire le texte des images
3. Sauvegarder les données extraites au format JSON

## Prérequis

- Python 3.x
- Poppler (pour pdf2image)
- Tesseract OCR

## Installation

1. Installer les dépendances Python :
```bash
pip install -r requirements.txt
```

2. Installer Poppler :
- Sur MacOS : `brew install poppler`
- Sur Linux : `sudo apt-get install poppler-utils`

3. Installer Tesseract :
- Sur MacOS : `brew install tesseract`
- Sur Linux : `sudo apt-get install tesseract-ocr`

## Utilisation

1. Exécutez le script :
```bash
python pdf_converter.py
```

2. Entrez le chemin de votre fichier PDF quand demandé

Le script créera un dossier `output` contenant :
- Les images de chaque page du PDF
- Un fichier `extracted_data.json` avec le texte extrait

## Format de sortie JSON

Le fichier JSON contient :
- Une liste de pages
- Pour chaque page :
  - Le numéro de page
  - Le texte extrait
  - Le chemin de l'image correspondante

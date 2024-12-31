
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import json
import pytesseract

def preprocess_image(image):
    """
    Prétraite l'image avec OpenCV pour améliorer la qualité du texte
    """
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Débruitage
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Amélioration du contraste avec CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Binarisation adaptative
    binary = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    return binary

def detect_text_regions(image):
    """
    Détecte les régions contenant du texte en utilisant OpenCV
    """
    # Appliquer un flou gaussien
    blur = cv2.GaussianBlur(image, (3, 3), 0)
    
    # Détection des contours avec Canny
    edges = cv2.Canny(blur, 100, 200)
    
    # Dilatation pour connecter les composants textuels
    kernel = np.ones((2,10), np.uint8)  # kernel horizontal pour connecter les lettres
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # Trouver les contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrer les contours par taille
    text_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filtrer les régions par rapport largeur/hauteur et taille minimale
        if w > 40 and 10 < h < 100 and w/h > 2:  # Probablement une ligne de texte
            text_regions.append((x, y, w, h))
    
    # Trier les régions de haut en bas
    text_regions.sort(key=lambda r: r[1])
    
    return text_regions

def extract_text_from_region(image, region):
    """
    Extrait le texte d'une région spécifique de l'image
    """
    x, y, w, h = region
    roi = image[y:y+h, x:x+w]
    text = pytesseract.image_to_string(roi, lang='fra', config='--psm 7')
    return text.strip()

def process_pdf(pdf_path, output_dir):
    """
    Traite le PDF et sauvegarde les images traitées
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Traitement du fichier : {os.path.basename(pdf_path)}")
    
    # Convertir le PDF en images
    images = convert_from_path(pdf_path)
    
    results = []
    for i, image in enumerate(images, start=1):
        print(f"\nPage {i}:")
        print("-" * 50)
        
        # Convertir l'image PIL en format OpenCV
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Prétraiter l'image
        processed = preprocess_image(image_cv)
        
        # Détecter les régions de texte
        text_regions = detect_text_regions(processed)
        
        # Extraire le texte de chaque région
        page_text = []
        for region in text_regions:
            text = extract_text_from_region(processed, region)
            if text:  # Ne garder que les régions avec du texte
                page_text.append(text)
                print(text)
        
        # Dessiner les régions détectées sur une copie de l'image originale
        output_image = image_cv.copy()
        for (x, y, w, h) in text_regions:
            cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Sauvegarder les images
        original_path = os.path.join(output_dir, f'page_{i}_original.png')
        processed_path = os.path.join(output_dir, f'page_{i}_processed.png')
        detected_path = os.path.join(output_dir, f'page_{i}_detected.png')
        
        cv2.imwrite(original_path, image_cv)
        cv2.imwrite(processed_path, processed)
        cv2.imwrite(detected_path, output_image)
        
        # Stocker les informations de la page
        page_info = {
            "page_number": i,
            "original_image": original_path,
            "processed_image": processed_path,
            "detected_image": detected_path,
            "text_regions": text_regions,
            "text_content": page_text
        }
        results.append(page_info)
    
    # Sauvegarder les résultats en JSON
    results_path = os.path.join(output_dir, 'text_regions.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump({"pages": results}, f, indent=4, ensure_ascii=False)
    
    print(f"\nTraitement terminé. Résultats sauvegardés dans {output_dir}")
    print(f"Nombre de pages traitées : {len(images)}")

if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"
    
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("Aucun fichier PDF trouvé dans le dossier input.")
    else:
        pdf_file = pdf_files[0]
        pdf_path = os.path.join(input_dir, pdf_file)
        process_pdf(pdf_path, output_dir)

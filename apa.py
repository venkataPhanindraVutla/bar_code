import sys
import cv2 as cv
from pyzbar.pyzbar import decode
import requests

OPENAI_API_KEY = "sk-sNceE_bpNEEcREeKQ9tIhHTpr-jZbEzr8LlyM3zzOUT3BlbkFJUMvvdXmUXJzu9S7XM0uhfUu4p4aaa9qebGII2lVjMA"
OPEN_FOOD_FACTS_API = "https://world.openfoodfacts.org/api/v0/product/{}.json"

def scan_barcode(image_path):
    image = cv.imread(image_path)
    barcodes = decode(image)
    if barcodes:
        return barcodes[0].data.decode('utf-8')
    return None

def get_product_info(barcode):
    response = requests.get(OPEN_FOOD_FACTS_API.format(barcode))
    if response.status_code == 200:
        product = response.json().get('product', {})
        return product.get('product_name'), product.get('ingredients_text')
    return None, None

def analyze_ingredients(ingredients):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {sk-sNceE_bpNEEcREeKQ9tIhHTpr-jZbEzr8LlyM3zzOUT3BlbkFJUMvvdXmUXJzu9S7XM0uhfUu4p4aaa9qebGII2lVjMA}"
    }
    
    prompt = f"Analyze the following cosmetic ingredients for potential harmfulness. List any harmful ingredients and explain why they might be concerning: {ingredients}"
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "Error in analyzing ingredients."

def main(image_path):
    # Scan barcode
    barcode = scan_barcode(image_path)
    if not barcode:
        print("No barcode found in the image.")
        return

    print(f"Barcode found: {barcode}")

    # Get product info
    product_name, ingredients = get_product_info(barcode)
    if not product_name or not ingredients:
        print(f"No product information found for barcode {barcode}.")
        return

    print(f"Product: {product_name}")
    print(f"Ingredients: {ingredients}")

    # Analyze ingredients
    analysis = analyze_ingredients(ingredients)

    print("\nAnalysis:")
    print(analysis)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_barcode_image>")
    else:
        image_path = sys.argv[1]
        main(image_path)
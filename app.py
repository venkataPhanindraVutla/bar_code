import tkinter as tk
from tkinter import filedialog, scrolledtext
import cv2 as cv
from pyzbar.pyzbar import decode
import requests
from PIL import Image, ImageTk
import cv2
# You need to sign up for these APIs and replace with your actual keys
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
        "Authorization": f"Bearer {OPENAI_API_KEY}"
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

class BarcodeApp:
    def __init__(self, master):
        self.master = master
        master.title("Barcode Ingredient Analyzer")
        
        self.label = tk.Label(master, text="Select an image with a product barcode:")
        self.label.pack()

        self.select_button = tk.Button(master, text="Select Image", command=self.select_image)
        self.select_button.pack()

        self.image_label = tk.Label(master)
        self.image_label.pack()

        self.result_text = scrolledtext.ScrolledText(master, height=20, width=60)
        self.result_text.pack()

    def select_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.process_image(file_path)

    def process_image(self, image_path):
        # Display the selected image
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        # Scan barcode
        barcode = scan_barcode(image_path)
        if not barcode:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No barcode found in the image. Please try another image.")
            return

        # Get product info
        product_name, ingredients = get_product_info(barcode)
        if not product_name or not ingredients:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"No product information found for barcode {barcode}.")
            return

        # Analyze ingredients
        analysis = analyze_ingredients(ingredients)

        # Display results
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Product: {product_name}\n\n")
        self.result_text.insert(tk.END, f"Ingredients: {ingredients}\n\n")
        self.result_text.insert(tk.END, f"Analysis:\n{analysis}")

root = tk.Tk()
app = BarcodeApp(root)
root.mainloop()
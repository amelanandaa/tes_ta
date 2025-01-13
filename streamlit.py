import streamlit as st
import numpy as np
import re
import pandas as pd
# import pytesseract
from PIL import Image
import requests

# Fungsi untuk memproses teks dengan regex
def process_text_with_regex(text):
    text = text.replace("=", "").replace(":", "").replace(".", "").replace("—", " ")
    discount_pattern = r"(.*?)(?:\((\d+[,\d]*)\))+\s*(\(\d+[,\d]*\))?"
    normal_pattern = r"(.*?)(?=\s+\d)\s+(\d+)\s+(\d[\d,]*)\s+(\d[\d,]*)$"
    extracted_data = []

    for line in text.split("\n"):
        line = line.strip()  # Bersihkan spasi di awal/akhir
        if "(" in line and ")" in line:  # Jika ada diskon (angka dalam tanda kurung)
            discount_match = re.search(discount_pattern, line)
            if discount_match:
                product_name = discount_match.group(1).strip()
                discount = discount_match.group(2).strip("()")  # Ambil angka dalam kurung
                extracted_data.append((product_name, "N/A", discount, "N/A"))
        else:  # Jika baris normal
            match = re.search(normal_pattern, line)
            if match:
                product_name = match.group(1).strip()
                quantity = int(match.group(2))
                harga = match.group(3)
                total_price = match.group(4)
                extracted_data.append((product_name, quantity, harga, total_price))
            else:
                pattern = r"(.*?)(?=\s+\d)\s+(\d+)\s+(\d[\d,]*)$"
                match = re.search(pattern, line)
                if match:
                    product_name = match.group(1).strip()
                    quantity = int(match.group(2))
                    harga = None
                    total_price = match.group(3)
                    extracted_data.append((product_name, quantity, harga, total_price))

    # Output hasil ke dataframe
    products = []
    for data in extracted_data:
        if len(data) == 4 and data[1] == "N/A":  # Baris dengan diskon
            product_name, _, discount, _ = data
            products.append({"Product": product_name, "Quantity": None, "Harga per Unit": None, "Total Price": None, "Discount": discount})
        else:  # Baris normal
            product_name, quantity, harga, total_price = data
            products.append({"Product": product_name, "Quantity": quantity, "Harga per Unit": harga, "Total Price": total_price, "Discount": None})

    return pd.DataFrame(products)

# # Fungsi untuk menangani upload gambar dan ekstraksi teks OCR
# def extract_text_from_image(uploaded_file):
#     image = Image.open(uploaded_file)
#     extracted_text = pytesseract.image_to_string(image, lang='eng')
#     return extracted_text, image

def ocr_space_url(filename, api_key='K89469847988957'):
    url = 'https://api.ocr.space/parse/image'
    with open(filename, 'rb') as file:
        r = requests.post(url, files={filename: file}, data={'apikey': api_key})
    return r.json()
    
    if result['IsErroredOnProcessing'] == False:
        # Mengambil teks hasil OCR dari response
        text = result['ParsedResults'][0]['ParsedText']
        return text
    else:
        print("OCR failed. Error:", result['ErrorMessage'])
        return None


# Fungsi utama untuk menjalankan aplikasi Streamlit
# def main():
#     st.title("OCR & Object Detection for Receipt Processing")

#     # Upload gambar
#     uploaded_file = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"])

#     if uploaded_file is not None:
#         # Ekstraksi teks dari gambar menggunakan OCR
#         extracted_text, image = extract_text_from_image(uploaded_file)

#         # Tampilkan gambar yang diupload
#         st.image(image, caption="Uploaded Image", use_column_width=True)

#         # Tampilkan teks hasil OCR
#         st.subheader("Extracted Text")
#         st.text(extracted_text)

#         # Proses teks dengan regex
#         processed_df = process_text_with_regex(extracted_text)

#         # Tampilkan hasil akhir sebagai dataframe
#         st.subheader("Final Data")
#         st.dataframe(processed_df)

# if __name__ == "__main__":
#     main()

st.title("OCR & Object Detection for Receipt Processing")

# Upload gambar
uploaded_file = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Simpan gambar sementara
    with open("uploaded_receipt.png", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Gunakan API OCR.space untuk ekstrak teks
    extracted_text = ocr_using_tesseract_api("uploaded_receipt.png", api_key='K89469847988957')

    if extracted_text:
        # Tampilkan teks hasil OCR
        st.subheader("Extracted Text")
        st.text(extracted_text)

        # Proses teks dengan regex
        processed_df = process_text_with_regex(extracted_text)

        # Tampilkan hasil akhir sebagai dataframe
        st.subheader("Final Data")
        st.dataframe(processed_df)


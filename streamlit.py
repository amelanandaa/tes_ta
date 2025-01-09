# -*- coding: utf-8 -*-
"""streamlit.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Qj38q_mfoH-E_572uPbKpU-y4CBTeNIY
"""

import streamlit as st
import cv2
import numpy as np
import torch
import re
import pandas as pd
from ultralytics import YOLO
import pytesseract
import gdown

# Download file model dari Google Drive
url = 'https://drive.google.com/file/d/1pdsS2ja2TDM2HWCKaM30PB_O1fxZKtk3/view?usp=drive_link'
output = 'model_yolo.pt'
gdown.download(url, output, quiet=False)

# Load model
model = YOLO(output)

# Fungsi untuk membaca teks dari ROI
def extract_text_with_tesseract(image, x_center, y_center, width, height):
    # Konversi bounding box YOLO (center format) ke Tesseract (corner format)
    x = int(x_center - (width / 2))
    y = int(y_center - (height / 2))
    w = int(width)
    h = int(height)

    # ROI berdasarkan bounding box
    roi = image[y:y + h, x:x + w]

    # Konfigurasi Tesseract
    config = "--psm 6"  # PSM 6 untuk segmen teks horizontal
    text = pytesseract.image_to_string(roi, config=config)
    return text

# Fungsi untuk proses regex
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

# Streamlit App
st.title("OCR & Object Detection for Receipt Processing")

# Upload gambar
uploaded_file = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Baca gambar dengan OpenCV
    image = Image.open(uploaded_file)
    image_np = np.array(image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Deteksi objek pada gambar dengan YOLO
    results = model(image_np)  # Proses gambar dengan YOLO
    result = results[0]  # Ambil hasil pertama

    # Tampilkan bounding boxes pada gambar
    result_plotted = result.plot()  # Gambar dengan bounding box
    st.image(result_plotted, caption="Detected Objects", use_column_width=True)

    # Ekstrak bounding boxes
    boxes_list = []
    for box in result.boxes.xywh.tolist():  # Format [x_center, y_center, width, height]
        boxes_list.append(box)

    # Ekstraksi teks dari setiap bounding box
    extracted_text = ""
    for x_center, y_center, width, height in boxes_list:
        text = extract_text_with_tesseract(image_np, x_center, y_center, width, height)
        extracted_text += text + "\n"

    # Tampilkan teks hasil OCR
    st.subheader("Extracted Text")
    st.text(extracted_text)

    # Proses teks dengan regex
    processed_df = process_text_with_regex(extracted_text)

    # Tampilkan hasil akhir sebagai dataframe
    st.subheader("Final Data")
    st.dataframe(processed_df)
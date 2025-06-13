import streamlit as st
from PIL import Image
import numpy as np
import io
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization

# Utility functions for encryption and decryption
def get_bin_char(a):
    x = [int(x) for x in bin(ord(a))[2:]]
    x = [0] * (7 - len(x)) + x
    return x

def get_bin_string(s):
    ret = []
    for char in s:
        ret += get_bin_char(char)
    ret += [0] * 7  # Null terminator
    return ret

def encode(I, s):
    x = get_bin_string(s)
    x = np.array(x, dtype=np.uint8)
    
    Iround = I - I % 2
    Iround = Iround.flatten()
    Iround[0:x.size] += x
    Iround = np.reshape(Iround, I.shape)
    return Iround

def decrypt(I):
    places = np.array([2 ** (6 - i) for i in range(7)])
    Idec = I.flatten()
    still_read = True
    i = 0
    s = ""
    while still_read:
        c = Idec[i:i + 7] % 2
        c = np.sum(places * c)
        
        if c == 0:
            still_read = False
        else:
            s += chr(c)
            
        i += 7
    return s

# Ciphers
def caesar_cipher_encrypt(text, shift):
    return ''.join(
        chr((ord(char) - 65 + shift) % 26 + 65) if char.isupper() else 
        chr((ord(char) - 97 + shift) % 26 + 97) if char.islower() else char
        for char in text
    )

def caesar_cipher_decrypt(text, shift):
    return caesar_cipher_encrypt(text, -shift)

def rail_fence_encrypt(text, key):
    fence = [[''] * len(text) for _ in range(key)]
    rail, var = 0, 1
    for char in text:
        fence[rail].append(char)
        rail += var
        if rail == 0 or rail == key - 1:
            var = -var
    return ''.join([''.join(row) for row in fence])

def rail_fence_decrypt(cipher, key):
    pattern = [[False] * len(cipher) for _ in range(key)]
    rail, var = 0, 1
    for i in range(len(cipher)):
        pattern[rail][i] = True
        rail += var
        if rail == 0 or rail == key - 1:
            var = -var

    index, result = 0, [''] * len(cipher)
    for r in range(key):
        for c in range(len(cipher)):
            if pattern[r][c]:
                result[c] = cipher[index]
                index += 1
    return ''.join(result)

# Streamlit app
st.title("Advanced Steganography with Encryption")

tab = st.selectbox("Choose Action", ["Encrypt", "Decrypt"])

if tab == "Encrypt":
    st.header("Encrypt Text in Image")
    image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    text = st.text_area("Enter text to encrypt")
    
    cipher_choice = st.selectbox("Choose a cipher method", ["None", "Caesar Cipher", "Rail Fence"])
    
    if cipher_choice == "Caesar Cipher":
        shift = st.number_input("Enter shift value for Caesar Cipher", min_value=1, max_value=25, value=3)
        text = caesar_cipher_encrypt(text, shift)
    elif cipher_choice == "Rail Fence":
        key = st.number_input("Enter key value for Rail Fence", min_value=2, max_value=10, value=3)
        text = rail_fence_encrypt(text, key)
    
    if st.button("Encrypt"):
        if image_file and text:
            # Open image and process
            image = Image.open(image_file).convert("RGB")
            image_np = np.array(image)
            
            # Encrypt text into image
            encrypted_image_np = encode(image_np, text)
            encrypted_image = Image.fromarray(encrypted_image_np)
            
            # Convert to bytes for download
            buffer = io.BytesIO()
            encrypted_image.save(buffer, format="PNG")
            buffer.seek(0)
            
            st.image(encrypted_image, caption="Encrypted Image")
            st.download_button("Download Encrypted Image", buffer, file_name="encrypted_image.png")
        else:
            st.warning("Please upload an image and enter text to encrypt.")

elif tab == "Decrypt":
    st.header("Decrypt Text from Image")
    encrypted_image_file = st.file_uploader("Upload an encrypted image", type=["png", "jpg", "jpeg"])
    cipher_choice = st.selectbox("Choose the cipher method used during encryption", ["None", "Caesar Cipher", "Rail Fence"])
    
    if st.button("Decrypt"):
        if encrypted_image_file:
            # Open image and process
            encrypted_image = Image.open(encrypted_image_file).convert("RGB")
            encrypted_image_np = np.array(encrypted_image)
            
            # Decrypt text from image
            decrypted_text = decrypt(encrypted_image_np)
            
            # Apply chosen cipher to decode text
            if cipher_choice == "Caesar Cipher":
                shift = st.number_input("Enter shift value for Caesar Cipher", min_value=1, max_value=25, value=3)
                decrypted_text = caesar_cipher_decrypt(decrypted_text, shift)
            elif cipher_choice == "Rail Fence":
                key = st.number_input("Enter key value for Rail Fence", min_value=2, max_value=10, value=3)
                decrypted_text = rail_fence_decrypt(decrypted_text, key)
            
            st.write("Decrypted Text:")
            st.text(decrypted_text)
        else:
            st.warning("Please upload an encrypted image.")

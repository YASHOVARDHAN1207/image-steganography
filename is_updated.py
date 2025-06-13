import streamlit as st
from PIL import Image
import numpy as np
import io

# Utility functions for steganography
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
def playfair_encrypt(text, key):
    key_matrix = create_playfair_matrix(key)
    text = prepare_playfair_text(text)
    encrypted = ""
    for i in range(0, len(text), 2):
        encrypted += playfair_encrypt_pair(text[i:i+2], key_matrix)
    return encrypted

def playfair_decrypt(text, key):
    key_matrix = create_playfair_matrix(key)
    decrypted = ""
    for i in range(0, len(text), 2):
        decrypted += playfair_decrypt_pair(text[i:i+2], key_matrix)
    return decrypted

def create_playfair_matrix(key):
    key = "".join(dict.fromkeys(key.upper().replace("J", "I")))
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    matrix = key + "".join([c for c in alphabet if c not in key])
    return [matrix[i:i+5] for i in range(0, 25, 5)]

def prepare_playfair_text(text):
    text = ''.join(filter(str.isalpha, text.upper().replace("J", "I")))
    prepared = ""
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i] != text[i + 1]:
            prepared += text[i] + text[i + 1]
            i += 2
        else:
            prepared += text[i] + "X"
            i += 1
    if len(prepared) % 2 != 0:
        prepared += "X"
    return prepared

def playfair_encrypt_pair(pair, key_matrix):
    row1, col1, row2, col2 = locate_pair(pair, key_matrix)
    if row1 == row2:
        return key_matrix[row1][(col1 + 1) % 5] + key_matrix[row2][(col2 + 1) % 5]
    elif col1 == col2:
        return key_matrix[(row1 + 1) % 5][col1] + key_matrix[(row2 + 1) % 5][col2]
    else:
        return key_matrix[row1][col2] + key_matrix[row2][col1]

def playfair_decrypt_pair(pair, key_matrix):
    row1, col1, row2, col2 = locate_pair(pair, key_matrix)
    if row1 == row2:
        return key_matrix[row1][(col1 - 1) % 5] + key_matrix[row2][(col2 - 1) % 5]
    elif col1 == col2:
        return key_matrix[(row1 - 1) % 5][col1] + key_matrix[(row2 - 1) % 5][col2]
    else:
        return key_matrix[row1][col2] + key_matrix[row2][col1]

def locate_pair(pair, key_matrix):
    row1, col1, row2, col2 = None, None, None, None
    for r, row in enumerate(key_matrix):
        for c, val in enumerate(row):
            if val == pair[0]:
                row1, col1 = r, c
            elif val == pair[1]:
                row2, col2 = r, c
    return row1, col1, row2, col2

def rail_fence_encrypt(text, key):
    fence = [[] for _ in range(key)]
    rail, var = 0, 1
    for char in text:
        fence[rail].append(char)
        rail += var
        if rail == 0 or rail == key - 1:
            var = -var
    return ''.join(''.join(row) for row in fence)

def rail_fence_decrypt(cipher, key):
    pattern = [[] for _ in range(key)]
    rail, var = 0, 1
    for _ in cipher:
        pattern[rail].append('*')
        rail += var
        if rail == 0 or rail == key - 1:
            var = -var

    index = 0
    for r in range(key):
        for c in range(len(cipher)):
            if pattern[r][c] == '*':
                pattern[r][c] = cipher[index]
                index += 1

    rail, var = 0, 1
    result = []
    for _ in cipher:
        result.append(pattern[rail].pop(0))
        rail += var
        if rail == 0 or rail == key - 1:
            var = -var
    return ''.join(result)

# Streamlit app
st.title("Advanced Steganography with Encryption")

tab = st.selectbox("Choose Action", ["Encrypt", "Decrypt"])

if tab == "Encrypt":
    st.header("Encrypt Text in Image")
    image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    text = st.text_area("Enter text to encrypt")
    
    cipher_choice = st.selectbox("Choose a cipher method", ["None", "Playfair Cipher", "Rail Fence"])
    
    if cipher_choice == "Playfair Cipher":
        key = st.text_input("Enter key for Playfair Cipher")
        if key:
            text = playfair_encrypt(text, key)
    elif cipher_choice == "Rail Fence":
        key = st.number_input("Enter key value for Rail Fence", min_value=2, max_value=10, value=3)
        text = rail_fence_encrypt(text, key)
    
    if st.button("Encrypt"):
        if image_file and text:
            image = Image.open(image_file).convert("RGB")
            image_np = np.array(image)
            encrypted_image_np = encode(image_np, text)
            encrypted_image = Image.fromarray(encrypted_image_np)
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
    cipher_choice = st.selectbox("Choose the cipher method used during encryption", ["None", "Playfair Cipher", "Rail Fence"])
    decryption_key = st.text_input("Enter the decryption key:", type="password")  # Secure input for the key
    
    if st.button("Decrypt"):
        if encrypted_image_file:
            if not decryption_key:
                st.warning("Please enter the decryption key.")
                st.stop()
            encrypted_image = Image.open(encrypted_image_file).convert("RGB")
            encrypted_image_np = np.array(encrypted_image)
            decrypted_text = decrypt(encrypted_image_np)
            
            if cipher_choice == "Playfair Cipher":
                try:
                    decrypted_text = playfair_decrypt(decrypted_text, decryption_key)
                except ValueError:
                    st.error("Decryption failed: Invalid Playfair key.")
                    st.stop()
            elif cipher_choice == "Rail Fence":
                try:
                    key = int(decryption_key)
                    decrypted_text = rail_fence_decrypt(decrypted_text, key)
                except ValueError:
                    st.error("Decryption failed: Rail Fence key must be numeric.")
                    st.stop()
            
            st.write("Decrypted Text:")
            st.text(decrypted_text)
        else:
            st.warning("Please upload an encrypted image.")

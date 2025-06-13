🖼️ Image Steganography Web App
This is a Streamlit-powered web application that performs image steganography — the practice of hiding secret messages within digital images. The app allows users to encode (hide) and decode (reveal) text messages using the Least Significant Bit (LSB) technique on .png images.

🔐 Features
🔏 Encode: Embed secret messages into images invisibly.

🔓 Decode: Retrieve hidden messages from stego images.

🧠 LSB Algorithm: Uses pixel-level manipulation to hide information securely.

🖼️ User-Friendly Interface: Interactive UI built with Streamlit.

🧰 No Image Quality Loss: Supports lossless .png images.

🚀 Getting Started
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/YASHOVARDHAN1207/image-steganography.git
cd image-steganography
2. Install Dependencies
Ensure you have Python 3.x installed. Then, install the required packages:

bash
Copy
Edit
pip install -r requirements.txt
If requirements.txt is not available, manually install Streamlit and Pillow:

bash
Copy
Edit
pip install streamlit pillow
3. Run the App
bash
Copy
Edit
streamlit run is_updated.py
🧪 Usage
Upload a .png image.

Enter the message to hide (for encoding) or extract (for decoding).

Click the Encode or Decode button.

Download the resulting image with hidden message (if encoded).

📂 Project Structure
is_updated.py – Final Streamlit app script.

IS_proj.py, IS_proj copy.py – Earlier versions or script backups.

get-pip.py – Optional pip installer if needed.

📌 Notes
Only .png images are supported to preserve data during embedding.

Message length is limited by the image size and capacity.

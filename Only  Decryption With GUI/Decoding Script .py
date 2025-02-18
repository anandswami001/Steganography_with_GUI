import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import base64
import hashlib

# Function to generate encryption key from password (ensuring it's 32 bytes)
def generate_key(password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hashed_password)

# Function to decode the hidden message from the image
def decode_image(image_path, password):
    try:
        img = Image.open(image_path)
        pixels = img.load()

        binary_message = ""
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))[:3]
                binary_message += format(r, '08b')[-1]
                binary_message += format(g, '08b')[-1]
                binary_message += format(b, '08b')[-1]

        byte_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        decoded_message = ''.join(chr(int(b, 2)) for b in byte_message)
        
        decrypted_message = Fernet(generate_key(password)).decrypt(decoded_message.encode()).decode()
        return decrypted_message
    except Exception as e:
        return str(e)

# Function to handle decode button click
def on_decode_button_click():
    password = entry_password.get()

    if not password:
        messagebox.showerror("Error", "Please enter the password.")
        return

    if not image_path.get():
        messagebox.showerror("Error", "Please select an image.")
        return

    decoded_message = decode_image(image_path.get(), password)
    if "Error" in decoded_message:
        messagebox.showerror("Error", decoded_message)
    else:
        messagebox.showinfo("Decoded Message", f"Your secret message is: {decoded_message}")
        on_reset_button_click()

# Function to handle reset button click
def on_reset_button_click():
    global img_label
    entry_password.delete(0, tk.END)
    image_path.set("")  # Clear the image path
    if img_label:
        img_label.destroy()
        img_label = None

# Function to handle image selection and display
def select_image():
    selected_image = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if selected_image:
        image_path.set(selected_image)

        img = Image.open(selected_image)
        img.thumbnail((200, 200))  # Resize for display
        img_display = ImageTk.PhotoImage(img)

        global img_label
        if img_label:
            img_label.config(image=img_display)
            img_label.image = img_display
        else:
            img_label = tk.Label(root, image=img_display)
            img_label.image = img_display
            img_label.pack(pady=10)

# GUI Setup
root = tk.Tk()
root.title("Image Steganography - Decode")

label_image = tk.Label(root, text="Select Image:")
label_image.pack(pady=5)

image_path = tk.StringVar()
entry_image = tk.Entry(root, textvariable=image_path, width=50)
entry_image.pack(pady=5)
button_select_image = tk.Button(root, text="Browse Image", command=select_image)
button_select_image.pack(pady=5)

label_password = tk.Label(root, text="Enter password:")
label_password.pack(pady=5)
entry_password = tk.Entry(root, width=50, show="*")
entry_password.pack(pady=5)

button_decode = tk.Button(root, text="Decode Message", command=on_decode_button_click)
button_decode.pack(pady=10)

button_reset = tk.Button(root, text="Reset", command=on_reset_button_click)
button_reset.pack(pady=10)

img_label = None
root.mainloop()

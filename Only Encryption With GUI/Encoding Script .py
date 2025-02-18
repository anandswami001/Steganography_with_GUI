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

# Function to encode a message into the image
def encode_image(image_path, message, password):
    try:
        img = Image.open(image_path)
        pixels = img.load()

        encrypted_message = Fernet(generate_key(password)).encrypt(message.encode()).decode()
        binary_message = ''.join(format(ord(char), '08b') for char in encrypted_message)

        if len(binary_message) > img.width * img.height * 3:
            raise Exception("Message is too large to be hidden in this image.")

        data_index = 0
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))[:3]
                r_bin = format(r, '08b')
                g_bin = format(g, '08b')
                b_bin = format(b, '08b')

                if data_index < len(binary_message):
                    r_bin = r_bin[:-1] + binary_message[data_index]
                    data_index += 1
                if data_index < len(binary_message):
                    g_bin = g_bin[:-1] + binary_message[data_index]
                    data_index += 1
                if data_index < len(binary_message):
                    b_bin = b_bin[:-1] + binary_message[data_index]
                    data_index += 1

                img.putpixel((x, y), (int(r_bin, 2), int(g_bin, 2), int(b_bin, 2)))

                if data_index >= len(binary_message):
                    break
            if data_index >= len(binary_message):
                break

        img.save("encoded_image.png")
        return "encoded_image.png"
    except Exception as e:
        return str(e)

# Function to handle encode button click
def on_encode_button_click():
    message = entry_message.get()
    password = entry_password.get()

    if not message or not password:
        messagebox.showerror("Error", "Please enter both message and password.")
        return

    if not image_path.get():
        messagebox.showerror("Error", "Please select an image.")
        return

    encoded_image_path = encode_image(image_path.get(), message, password)
    if "encoded_image.png" in encoded_image_path:
        messagebox.showinfo("Success", "Message hidden successfully. Image saved as encoded_image.png.")
        on_reset_button_click()
    else:
        messagebox.showerror("Error", encoded_image_path)

# Function to handle reset button click
def on_reset_button_click():
    global img_label  # Declare img_label as global
    entry_message.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    image_path.set("")  # Clear the image path
    if img_label:
        img_label.destroy()  # Remove the image label properly
        img_label = None  # Reset the global variable

# Function to handle image selection and display
def select_image():
    selected_image = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if selected_image:
        image_path.set(selected_image)

        # Open and display the image on the GUI
        img = Image.open(selected_image)
        img.thumbnail((200, 200))  # Resize for display
        img_display = ImageTk.PhotoImage(img)

        global img_label  # Make sure to reference the global variable
        if img_label:
            img_label.config(image=img_display)
            img_label.image = img_display  # Keep the reference to the image object
        else:
            img_label = tk.Label(root, image=img_display)
            img_label.image = img_display  # Keep the reference to the image object
            img_label.pack(pady=10)

# GUI Setup
root = tk.Tk()
root.title("Image Steganography - Encode")

label_image = tk.Label(root, text="Select Image:")
label_image.pack(pady=5)

image_path = tk.StringVar()  # Variable to hold the image path
entry_image = tk.Entry(root, textvariable=image_path, width=50)
entry_image.pack(pady=5)
button_select_image = tk.Button(root, text="Browse Image", command=select_image)
button_select_image.pack(pady=5)

label_message = tk.Label(root, text="Enter your message:")
label_message.pack(pady=5)
entry_message = tk.Entry(root, width=50)
entry_message.pack(pady=5)

label_password = tk.Label(root, text="Enter password:")
label_password.pack(pady=5)
entry_password = tk.Entry(root, width=50, show="*")
entry_password.pack(pady=5)

button_encode = tk.Button(root, text="Encode Message", command=on_encode_button_click)
button_encode.pack(pady=10)

button_reset = tk.Button(root, text="Reset", command=on_reset_button_click)
button_reset.pack(pady=10)

img_label = None
root.mainloop()

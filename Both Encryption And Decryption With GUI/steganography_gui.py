import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import base64
import hashlib

# Function to generate encryption key from password (ensuring it's 32 bytes)
def generate_key(password):
    # Use SHA-256 to create a 32-byte hash from the password
    hashed_password = hashlib.sha256(password.encode('utf-8')).digest()
    # Base64 URL-safe encode the 32-byte hash (Fernet key requirement)
    return base64.urlsafe_b64encode(hashed_password)

# Function to encode a message into the image
def encode_image(image_path, message, password):
    try:
        # Open the image
        img = Image.open(image_path)
        pixels = img.load()

        # Prepare the message by encoding it and converting to binary
        encrypted_message = Fernet(generate_key(password)).encrypt(message.encode()).decode()
        binary_message = ''.join(format(ord(char), '08b') for char in encrypted_message)

        # Check if the image is large enough to hide the message
        if len(binary_message) > img.width * img.height * 3:
            raise Exception("Message is too large to be hidden in this image.")

        data_index = 0
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))[:3]  # Ensure we only get RGB (ignoring alpha)

                r_bin = format(r, '08b')
                g_bin = format(g, '08b')
                b_bin = format(b, '08b')

                # Modify the least significant bit of each color channel
                if data_index < len(binary_message):
                    r_bin = r_bin[:-1] + binary_message[data_index]
                    data_index += 1
                if data_index < len(binary_message):
                    g_bin = g_bin[:-1] + binary_message[data_index]
                    data_index += 1
                if data_index < len(binary_message):
                    b_bin = b_bin[:-1] + binary_message[data_index]
                    data_index += 1

                # Update the pixel with the new binary values
                img.putpixel((x, y), (int(r_bin, 2), int(g_bin, 2), int(b_bin, 2)))

                if data_index >= len(binary_message):
                    break
            if data_index >= len(binary_message):
                break

        # Save the image with the hidden message
        img.save("encoded_image.png")
        return "encoded_image.png"
    except Exception as e:
        return str(e)

# Function to decode the hidden message from the image
def decode_image(image_path, password):
    try:
        img = Image.open(image_path)
        pixels = img.load()

        binary_message = ""
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))[:3]  # Ensure we only get RGB (ignoring alpha)
                binary_message += format(r, '08b')[-1]
                binary_message += format(g, '08b')[-1]
                binary_message += format(b, '08b')[-1]

        # Convert binary message to string
        byte_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        decoded_message = ''.join(chr(int(b, 2)) for b in byte_message)
        
        # Decrypt the message using the password
        decrypted_message = Fernet(generate_key(password)).decrypt(decoded_message.encode()).decode()
        return decrypted_message
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
        on_reset_button_click()  # Reset fields after successful encoding
    else:
        messagebox.showerror("Error", encoded_image_path)

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
        messagebox.showinfo("Decoded Message", f"Your secret message is: {decoded_message}")  # Show the message in the required format
        on_reset_button_click()  # Reset fields after successful decoding

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
        image_path.set(selected_image)  # Update image path entry

        # Open and display the image on the GUI
        img = Image.open(selected_image)
        img.thumbnail((200, 200))  # Resize for display
        img_display = ImageTk.PhotoImage(img)

        # If there's already an image displayed, remove it
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
root.title("Image Steganography")

# Image Selection Label and Button (Moved to the top)
label_image = tk.Label(root, text="Select Image:")
label_image.pack(pady=5)

image_path = tk.StringVar()  # Variable to hold the image path
entry_image = tk.Entry(root, textvariable=image_path, width=50)
entry_image.pack(pady=5)
button_select_image = tk.Button(root, text="Browse Image", command=select_image)
button_select_image.pack(pady=5)

# Message Label and Entry
label_message = tk.Label(root, text="Enter your message:")
label_message.pack(pady=5)
entry_message = tk.Entry(root, width=50)
entry_message.pack(pady=5)

# Password Label and Entry
label_password = tk.Label(root, text="Enter password:")
label_password.pack(pady=5)
entry_password = tk.Entry(root, width=50, show="*")
entry_password.pack(pady=5)

# Buttons
button_encode = tk.Button(root, text="Encode Message", command=on_encode_button_click)
button_encode.pack(pady=10)

button_decode = tk.Button(root, text="Decode Message", command=on_decode_button_click)
button_decode.pack(pady=10)

button_reset = tk.Button(root, text="Reset", command=on_reset_button_click)
button_reset.pack(pady=10)

# Initialize img_label as None to prevent errors
img_label = None

# Run the GUI
root.mainloop()

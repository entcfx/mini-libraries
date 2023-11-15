import os
import hashlib
import sys
import random
import time
import ctypes
import stat
import secrets
import base64

# A main class for our custom encryption alogrythm called EntCrypt
class EntCrypt:
    def __init__(self):
        # Generate a random key
        self.raw_key = secrets.token_bytes(64)
        self.key = hashlib.sha256(self.raw_key).digest()

    def encrypt_plaintext(self, bin_plaintext):
        bin_key = bytes(self.key)
        
        encrypted_bin = bytearray()
        for i in range(len(bin_plaintext)):
            encrypted_bin.append(bin_plaintext[i] ^ bin_key[i % len(bin_key)])
        
        return bytes(encrypted_bin)

    def decrypt_plaintext(self, encrypted_bin):
        bin_key = bytes(self.key)

        decrypted_bin = bytearray()
        for i in range(len(encrypted_bin)):
            decrypted_bin.append(encrypted_bin[i] ^ bin_key[i % len(bin_key)])
        
        return bytes(decrypted_bin)


#
# File encryption and decryption using entcrypt
#
#
def ecrypt_encrypt_file(file_path, entcrypt_object):
    try:
        # Check if entcrypt_object is provided and is an instance of EntCrypt
        if not entcrypt_object or not isinstance(entcrypt_object, EntCrypt):
            raise ValueError("Invalid or missing EntCrypt object.")

        with open(file_path, 'rb') as file:
            plaintext = file.read()

        encrypted_text = entcrypt_object.encrypt_plaintext(plaintext)

        encrypted_file_path = file_path + ".entcrypt"
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_text)

        print(f"File encrypted and saved to: {encrypted_file_path}")

    except FileNotFoundError:
        print(f"Error: File not found at path {file_path}")

    except ValueError as ve:
        print(f"Error: {ve}")

    except Exception as e:
        print(f"An error occurred during encryption: {e}")



def ecrypt_decrypt_file(file_path, entcrypt_object):
    try:
        # Check if entcrypt_object is provided and is an instance of EntCrypt
        if not entcrypt_object or not isinstance(entcrypt_object, EntCrypt):
            raise ValueError("Invalid or missing EntCrypt object.")

        with open(file_path, 'rb') as encrypted_file:
            ciphertext = encrypted_file.read()

        decrypted_text = entcrypt_object.decrypt_plaintext(ciphertext)

        # Remove the ".entcrypt" extension from the original file name
        decrypted_file_path = file_path[:-8] if file_path.endswith(".entcrypt") else file_path + ".decrypted"

        with open(decrypted_file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_text)

        print(f"File decrypted and saved to: {decrypted_file_path}")

    except FileNotFoundError:
        print(f"Error: Encrypted file not found at path {file_path}")

    except ValueError as ve:
        print(f"Error: {ve}")

    except Exception as e:
        print(f"An error occurred during decryption: {e}")


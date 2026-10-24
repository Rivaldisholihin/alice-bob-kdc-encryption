import os
import json
import socket
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KDC_HOST = os.getenv("KDC_HOST", "192.168.1.10")
KDC_PORT = int(os.getenv("KDC_PORT", "5000"))
BOB_HOST = os.getenv("BOB_HOST", "192.168.1.12")
BOB_PORT = int(os.getenv("BOB_PORT", "5002"))

def key_from_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} belum diatur.")
    key = bytes.fromhex(value)
    if len(key) != 32:
        raise RuntimeError(f"{name} harus berisi kunci 32 byte (64 karakter heksadesimal).")
    return key

def send_json(conn, data):
    conn.sendall(json.dumps(data).encode("utf-8") + b"\n")

def recv_json(conn):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = conn.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > 1_000_000:
            raise ValueError("Respons terlalu besar.")
    if not data:
        raise ValueError("Respons kosong.")
    return json.loads(data.decode("utf-8"))

def decrypt_json(key, package):
    nonce = base64.b64decode(package["nonce"])
    ciphertext = base64.b64decode(package["ciphertext"])
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))

def main():
    alice_master_key = key_from_env("ALICE_MASTER_KEY")
    message = input("Masukkan pesan untuk Bob: ")

    with socket.create_connection((KDC_HOST, KDC_PORT), timeout=10) as conn:
        send_json(conn, {"type": "REQUEST_SESSION_KEY", "from": "Alice", "to": "Bob"})
        response = recv_json(conn)

    if response.get("status") != "ok":
        raise RuntimeError(f"KDC menolak permintaan: {response.get('message', 'tidak diketahui')}")

    material = decrypt_json(alice_master_key, response["wrapped"])
    session_key = base64.b64decode(material["session_key"])
    ticket_for_bob = material["ticket_for_bob"]

    nonce = os.urandom(12)
    ciphertext = AESGCM(session_key).encrypt(nonce, message.encode("utf-8"), None)
    packet = {
        "ticket_for_bob": ticket_for_bob,
        "message_nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

    with socket.create_connection((BOB_HOST, BOB_PORT), timeout=10) as conn:
        send_json(conn, packet)
        result = recv_json(conn)

    print("[Alice] Session key diterima dan berhasil dibuka.")
    print("[Alice] Pesan terenkripsi telah dikirim ke Bob.")
    print("[Bob] Respons:", result.get("message", "Tidak ada respons."))

if __name__ == "__main__":
    main()

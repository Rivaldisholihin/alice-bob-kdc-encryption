import os
import json
import socket
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = os.getenv("BOB_HOST", "0.0.0.0")
PORT = int(os.getenv("BOB_PORT", "5002"))

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
            raise ValueError("Paket terlalu besar.")
    if not data:
        raise ValueError("Paket kosong.")
    return json.loads(data.decode("utf-8"))

def decrypt_json(key, package):
    nonce = base64.b64decode(package["nonce"])
    ciphertext = base64.b64decode(package["ciphertext"])
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))

def handle(conn, address, bob_master_key):
    with conn:
        try:
            packet = recv_json(conn)
            ticket = decrypt_json(bob_master_key, packet["ticket_for_bob"])
            if ticket.get("from") != "Alice" or ticket.get("to") != "Bob":
                raise ValueError("Tiket tidak ditujukan kepada Bob.")

            session_key = base64.b64decode(ticket["session_key"])
            nonce = base64.b64decode(packet["message_nonce"])
            ciphertext = base64.b64decode(packet["ciphertext"])
            plaintext = AESGCM(session_key).decrypt(nonce, ciphertext, None).decode("utf-8")

            print(f"\n[Bob] Pesan dari Alice ({address}): {plaintext}")
            send_json(conn, {"status": "ok", "message": "Pesan berhasil didekripsi."})
        except Exception as exc:
            print(f"[Bob] Gagal memproses pesan dari {address}: {exc}")
            try:
                send_json(conn, {"status": "error", "message": "Pesan atau tiket tidak valid."})
            except Exception:
                pass

def main():
    bob_master_key = key_from_env("BOB_MASTER_KEY")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[Bob] Menunggu pesan pada {HOST}:{PORT}")
        while True:
            conn, address = server.accept()
            handle(conn, address, bob_master_key)

if __name__ == "__main__":
    main()

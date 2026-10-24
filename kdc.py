import os
import json
import socket
import secrets
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = os.getenv("KDC_HOST", "0.0.0.0")
PORT = int(os.getenv("KDC_PORT", "5000"))

def key_from_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} belum diatur.")
    try:
        key = bytes.fromhex(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} harus berupa 64 karakter heksadesimal.") from exc
    if len(key) != 32:
        raise RuntimeError(f"{name} harus berisi kunci 32 byte (64 karakter heksadesimal).")
    return key

def encrypt_json(key, data):
    nonce = os.urandom(12)
    plaintext = json.dumps(data).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    return {"nonce": base64.b64encode(nonce).decode(), "ciphertext": base64.b64encode(ciphertext).decode()}

def recv_json(conn):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = conn.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > 1_000_000:
            raise ValueError("Permintaan terlalu besar.")
    if not data:
        raise ValueError("Permintaan kosong.")
    return json.loads(data.decode("utf-8"))

def send_json(conn, data):
    conn.sendall(json.dumps(data).encode("utf-8") + b"\n")

def handle(conn, address, alice_key, bob_key):
    with conn:
        try:
            request = recv_json(conn)
            if request.get("type") != "REQUEST_SESSION_KEY" or request.get("from") != "Alice":
                send_json(conn, {"status": "error", "message": "Permintaan tidak valid."})
                return

            session_key = AESGCM.generate_key(bit_length=256)
            ticket_for_bob = encrypt_json(bob_key, {
                "from": "Alice",
                "to": "Bob",
                "session_key": base64.b64encode(session_key).decode()
            })
            response_for_alice = encrypt_json(alice_key, {
                "session_key": base64.b64encode(session_key).decode(),
                "ticket_for_bob": ticket_for_bob
            })
            send_json(conn, {"status": "ok", "wrapped": response_for_alice})
            print(f"[KDC] Session key dibuat dan dikirim kepada Alice; tiket Bob disertakan. Klien: {address}")
        except Exception as exc:
            try:
                send_json(conn, {"status": "error", "message": str(exc)})
            except Exception:
                pass
            print(f"[KDC] Permintaan gagal dari {address}: {exc}")

def main():
    alice_key = key_from_env("ALICE_MASTER_KEY")
    bob_key = key_from_env("BOB_MASTER_KEY")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[KDC] Berjalan pada {HOST}:{PORT}")
        while True:
            conn, address = server.accept()
            handle(conn, address, alice_key, bob_key)

if __name__ == "__main__":
    main()

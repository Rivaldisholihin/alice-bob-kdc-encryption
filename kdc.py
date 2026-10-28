import os
import json
import socket
import secrets
from aes_manual import AES128Manual

HOST = os.getenv("KDC_HOST", "0.0.0.0")
PORT = int(os.getenv("KDC_PORT", "5000"))

ALICE_MASTER_KEY = b"AliceMasterKey12" # 16-byte ASCII
BOB_MASTER_KEY   = b"BobMasterKey1234" # 16-byte ASCII

def send_json(conn, data):
    conn.sendall(json.dumps(data).encode("utf-8") + b"\n")

def recv_json(conn):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = conn.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
    return json.loads(data.decode("utf-8"))

def handle_client(conn, address):
    global ALICE_MASTER_KEY, BOB_MASTER_KEY
    with conn:
        try:
            req = recv_json(conn)
            if req.get("type") == "CHANGE_KEYS":
                ALICE_MASTER_KEY = req["alice_key"].encode('utf-8')[:16]
                BOB_MASTER_KEY = req["bob_key"].encode('utf-8')[:16]
                send_json(conn, {"status": "ok", "msg": "Master Keys Updated!"})
                print("[KDC] Master Keys berhasil diubah via menu interaktif.")
                return

            if req.get("type") == "REQUEST_SESSION_KEY":
                sender = req["from"]
                target = req["to"]
                
                # Buat Session Key acak (16 Byte) & IV (16 Byte)
                session_key = secrets.token_bytes(16)
                iv = secrets.token_bytes(16)

                aes_bob = AES128Manual(BOB_MASTER_KEY)
                ticket_payload = f"{sender}|{target}|{session_key.hex()}|{iv.hex()}"
                ticket_for_bob = aes_bob.encrypt_cbc(ticket_payload, iv)

                aes_alice = AES128Manual(ALICE_MASTER_KEY)
                alice_payload = f"{session_key.hex()}|{iv.hex()}|{ticket_for_bob}"
                wrapped_response = aes_alice.encrypt_cbc(alice_payload, iv)

                send_json(conn, {
                    "status": "ok",
                    "iv_hex": iv.hex(),
                    "wrapped": wrapped_response
                })
                print(f"[KDC] Session key dibuat untuk {sender} -> {target}")

        except Exception as e:
            print(f"[KDC] Error: {e}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[KDC Server Ready] Berjalan pada {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    main()
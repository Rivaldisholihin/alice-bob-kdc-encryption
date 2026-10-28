import os
import json
import socket
import threading
from aes_manual import AES128Manual

KDC_HOST = os.getenv("KDC_HOST", "127.0.0.1")
KDC_PORT = int(os.getenv("KDC_PORT", "5000"))
MY_HOST  = os.getenv("ALICE_HOST", "0.0.0.0")
MY_PORT  = int(os.getenv("ALICE_PORT", "5001"))
BOB_HOST = os.getenv("BOB_HOST", "127.0.0.1")
BOB_PORT = int(os.getenv("BOB_PORT", "5002"))

ALICE_MASTER_KEY = "AliceMasterKey12" # Format ASCII

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

def start_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((MY_HOST, MY_PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                pkt = recv_json(conn)
                ticket_hex = pkt["ticket"]
                iv_hex = pkt["iv_hex"]
                ciphertext_hex = pkt["ciphertext"]
                
                # Dekripsi Tiket untuk Alice
                aes_m = AES128Manual(ALICE_MASTER_KEY.encode('utf-8'))
                ticket_plain = aes_m.decrypt_cbc(ticket_hex, bytes.fromhex(iv_hex))
                sender, target, session_key_hex, _ = ticket_plain.split("|")
                
                # Dekripsi Pesan Utama
                aes_session = AES128Manual(bytes.fromhex(session_key_hex))
                msg = aes_session.decrypt_cbc(ciphertext_hex, bytes.fromhex(iv_hex))
                
                print(f"\n\n[PESAN MASUK dari {sender}]: {msg}")
                print(f"[Ciphertext Hex]: {ciphertext_hex}")
                print("\nPilihan Menu (1: Kirim Pesan, 2: Ganti Key): ", end="")

def send_message():
    global ALICE_MASTER_KEY
    # 1. Request Session Key ke KDC
    with socket.create_connection((KDC_HOST, KDC_PORT)) as conn:
        send_json(conn, {"type": "REQUEST_SESSION_KEY", "from": "Alice", "to": "Bob"})
        res = recv_json(conn)
    
    iv = bytes.fromhex(res["iv_hex"])
    aes_m = AES128Manual(ALICE_MASTER_KEY.encode('utf-8'))
    unwrapped = aes_m.decrypt_cbc(res["wrapped"], iv)
    session_key_hex, iv_hex, ticket_for_bob = unwrapped.split("|")
    
    pesan = input("Masukkan pesan ASCII untuk Bob: ")
    aes_session = AES128Manual(bytes.fromhex(session_key_hex))
    ciphertext_hex = aes_session.encrypt_cbc(pesan, bytes.fromhex(iv_hex))

    # 2. Kirim ke Bob
    with socket.create_connection((BOB_HOST, BOB_PORT)) as conn:
        send_json(conn, {
            "ticket": ticket_for_bob,
            "iv_hex": iv_hex,
            "ciphertext": ciphertext_hex
        })
    print(f"[TERKIRIM] Ciphertext Hex: {ciphertext_hex}")

def main():
    global ALICE_MASTER_KEY
    threading.Thread(target=start_listener, daemon=True).start()
    print(f"[Alice Ready] Port: {MY_PORT}")
    
    while True:
        print("\n--- MENU ALICE ---")
        print("1. Kirim Pesan ke Bob")
        print("2. Ubah Master Key (Interaktif)")
        print("3. Keluar")
        pilih = input("Pilihan: ")
        
        if pilih == "1":
            try:
                send_message()
            except Exception as e:
                print(f"[Error]: {e}")
        elif pilih == "2":
            new_key = input("Masukkan Master Key ASCII Baru (16 Karakter): ")
            ALICE_MASTER_KEY = new_key
            print(f"Master Key Alice diubah menjadi: {ALICE_MASTER_KEY}")
        elif pilih == "3":
            break

if __name__ == "__main__":
    main()
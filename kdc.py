import os
import json
import socket
import secrets
from aes_manual import AES128Manual

HOST = os.getenv("KDC_HOST", "0.0.0.0")
PORT = int(os.getenv("KDC_PORT", "5000"))


ALICE_MASTER_KEY = b"AliceMasterKey12"  # 16-byte ASCII (AES-128)
BOB_MASTER_KEY = b"BobMasterKey1234"    # 16-byte ASCII (AES-128)


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
            raise ValueError("Request too large")
    if not data:
        raise ValueError("Empty request")
    return json.loads(data.decode("utf-8"))


def make_distribution(sender: str, target: str):
    """Return requester-wrapped session key and target-encrypted ticket."""
    if sender == "Alice" and target == "Bob":
        requester_key = ALICE_MASTER_KEY
        recipient_key = BOB_MASTER_KEY
    elif sender == "Bob" and target == "Alice":
        requester_key = BOB_MASTER_KEY
        recipient_key = ALICE_MASTER_KEY
    else:
        raise ValueError("Only Alice->Bob or Bob->Alice is supported")

    session_key = secrets.token_bytes(16)  # AES-128 session key
    iv = secrets.token_bytes(16)            # AES block size = 16 bytes
    iv_hex = iv.hex()

    ticket_payload = f"{sender}|{target}|{session_key.hex()}|{iv_hex}"
    ticket_for_target = AES128Manual(recipient_key).encrypt_cbc(ticket_payload, iv)

    requester_payload = f"{session_key.hex()}|{iv_hex}|{ticket_for_target}"
    wrapped_for_requester = AES128Manual(requester_key).encrypt_cbc(requester_payload, iv)
    return {"status": "ok", "iv_hex": iv_hex, "wrapped": wrapped_for_requester}


def handle_client(conn, address):
    global ALICE_MASTER_KEY, BOB_MASTER_KEY
    with conn:
        try:
            req = recv_json(conn)
            if req.get("type") == "CHANGE_KEYS":
                alice_key = req.get("alice_key", "").encode("ascii", errors="strict")
                bob_key = req.get("bob_key", "").encode("ascii", errors="strict")
                if len(alice_key) != 16 or len(bob_key) != 16:
                    raise ValueError("Both master keys must be exactly 16 ASCII bytes")
                ALICE_MASTER_KEY, BOB_MASTER_KEY = alice_key, bob_key
                send_json(conn, {"status": "ok", "msg": "Master keys updated"})
                print(f"[KDC] Master keys updated by {address}")
                return

            if req.get("type") != "REQUEST_SESSION_KEY":
                raise ValueError("Unsupported request type")

            sender, target = req.get("from"), req.get("to")
            response = make_distribution(sender, target)
            send_json(conn, response)
            print(f"[KDC] Session key generated for {sender} -> {target}; client={address}")
        except Exception as exc:
            try:
                send_json(conn, {"status": "error", "message": str(exc)})
            except Exception:
                pass
            print(f"[KDC] Error from {address}: {exc}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[KDC Server Ready] Listening on {HOST}:{PORT}")
        while True:
            conn, address = server.accept()
            handle_client(conn, address)


if __name__ == "__main__":
    main()

# AES-128 Key Distribution Center (KDC)

## 1. Project Description

This project implements a symmetric cryptographic communication system using **AES-128 (Advanced Encryption Standard)** and a **Key Distribution Center (KDC)**.

The system enables two clients, Alice and Bob, to exchange encrypted messages securely with the assistance of a trusted third party (KDC).

The KDC generates a random Session Key and distributes it to Alice and Bob using their respective Master Keys. After obtaining the same Session Key, Alice and Bob can communicate using AES-128 encryption.

This implementation uses the **Cipher Block Chaining (CBC)** mode of operation and a manually implemented AES-128 algorithm.

## 2. Project Objectives

- Implement AES-128 encryption and decryption manually.
- Understand AES key expansion and its encryption rounds.
- Implement the Cipher Block Chaining (CBC) mode.
- Build a Key Distribution Center for Session Key generation and distribution.
- Establish secure communication between Alice and Bob.
- Demonstrate communication using three different IP addresses.
- Understand the role of Master Keys and Session Keys in symmetric cryptography.

## 3. System Architecture

The system consists of three main entities:

| Entity | Role | Default Port |
|---|---|---|
| KDC | Generates and distributes Session Keys | 5000 |
| Alice | Client that sends and receives encrypted messages | 5001 |
| Bob | Client that sends and receives encrypted messages | 5002 |

### Communication Architecture

```text
             +----------------+
             |      KDC       |
             |  Port: 5000    |
             |                |
             | Session Key    |
             | Generation     |
             +----------------+
                 /        \
                /          \
       Master Key          Master Key
              /              \
             /                \
    +---------------+   +---------------+
    |     ALICE     |   |      BOB      |
    |   Port: 5001  |   |   Port: 5002  |
    +---------------+   +---------------+
             \                 /
              \               /
               Encrypted Message
                 AES-128 CBC
```

Each entity can act as a sender or receiver.

Supported communication:
- Alice → Bob
- Bob → Alice

## 4. Cryptographic Implementation

### 4.1 AES-128

AES-128 is a symmetric block cipher that uses:
- Block size: 128 bits (16 bytes).
- Key size: 128 bits (16 bytes).
- Number of rounds: 10.

The implementation includes the following AES operations:

1. SubBytes
2. ShiftRows
3. MixColumns
4. AddRoundKey
5. Key Expansion

The final encryption round does not include MixColumns.

### 4.2 Cipher Block Chaining (CBC)

CBC is the block cipher operation mode used in this project.

During encryption, each plaintext block is XORed with the previous ciphertext block before being encrypted.

The first block uses an Initialization Vector (IV).

Encryption formula:

```text
C1 = AES(K, P1 XOR IV)

C2 = AES(K, P2 XOR C1)
```

Where:
- K = Encryption Key
- P = Plaintext
- C = Ciphertext
- IV = Initialization Vector

The implementation also uses PKCS7 padding to ensure that plaintext data fits the AES block size.

### 4.3 Key Distribution

The system uses two types of cryptographic keys:

**Master Key**
- Alice and KDC share Alice's Master Key.
- Bob and KDC share Bob's Master Key.
- Used to protect the Session Key distribution.

**Session Key**
- Generated randomly by KDC.
- Used by Alice and Bob for message encryption and decryption.
- Has a length of 128 bits (16 bytes).

## 5. Key Distribution Process

The communication process follows these steps:

1. Alice requests a Session Key from KDC for communication with Bob.
2. KDC generates a random Session Key and IV.
3. KDC encrypts a ticket containing the sender, recipient, Session Key, and IV using Bob's Master Key.
4. KDC encrypts the Session Key and ticket using Alice's Master Key.
5. Alice decrypts the response using her Master Key and obtains the Session Key and Bob's encrypted ticket.
6. Alice encrypts her message using the Session Key.
7. Alice sends the encrypted message and ticket to Bob.
8. Bob decrypts the ticket using his Master Key.
9. Bob obtains the Session Key and decrypts Alice's message.

The same process applies when Bob communicates with Alice.

## 6. Project Structure

```text
AES-KDC-Project/
│
├── aes_manual.py
│
├── kdc.py
│
├── alice.py
│
├── bob.py
│
└── README.md
```

### File Descriptions

| File | Description |
|---|---|
| `aes_manual.py` | Contains the manual AES-128 encryption and decryption implementation, including CBC mode and key expansion. |
| `kdc.py` | Implements the Key Distribution Center, Session Key generation, and key distribution. |
| `alice.py` | Implements Alice's client, including Session Key requests, message encryption, and decryption. |
| `bob.py` | Implements Bob's client, including Session Key requests, message encryption, and decryption. |
| `README.md` | Provides project documentation and execution instructions. |

## 7. System Requirements

- Python 3.x
- Three computers or devices connected to the same network.
- Network connectivity between Alice, Bob, and KDC.
- TCP ports 5000, 5001, and 5002 must be accessible.
- No additional Python packages are required.

## 8. Installation and Configuration

### Step 1: Prepare the Project

Copy all Python files into the project directory on the respective computers.

### Step 2: Configure IP Addresses

The practical assignment requires three different IP addresses.

Example network configuration:

| Device | IP Address | Port |
|---|---|---|
| KDC | 192.168.1.10 | 5000 |
| Alice | 192.168.1.11 | 5001 |
| Bob | 192.168.1.12 | 5002 |

Replace the example IP addresses with the actual IP addresses of your devices.

### Step 3: Configure Environment Variables

**On the KDC computer:**

```powershell
$env:KDC_HOST="0.0.0.0"
$env:KDC_PORT="5000"
```

**On the Alice computer:**

```powershell
$env:KDC_HOST="192.168.1.10"
$env:KDC_PORT="5000"
$env:ALICE_HOST="0.0.0.0"
$env:ALICE_PORT="5001"
$env:BOB_HOST="192.168.1.12"
$env:BOB_PORT="5002"
```

**On the Bob computer:**

```powershell
$env:KDC_HOST="192.168.1.10"
$env:KDC_PORT="5000"
$env:BOB_HOST="0.0.0.0"
$env:BOB_PORT="5002"
$env:ALICE_HOST="192.168.1.11"
$env:ALICE_PORT="5001"
```

## 9. Running the Application

Start the programs in the following order.

**Terminal 1 – KDC**

```bash
python kdc.py
```

Expected output:

```text
[KDC Server Ready] Listening on 0.0.0.0:5000
```

**Terminal 2 – Alice**

```bash
python alice.py
```

Expected output:

```text
[Alice Ready] Port: 5001

--- MENU ALICE ---
1. Kirim Pesan ke Bob
2. Ubah Master Key (Interaktif)
3. Keluar
```

**Terminal 3 – Bob**

```bash
python bob.py
```

Expected output:

```text
[Bob Ready] Port: 5002

--- MENU BOB ---
1. Kirim Pesan ke Alice
2. Ubah Master Key (Interaktif)
3. Keluar
```

## 10. How to Use

### Sending a Message from Alice to Bob

1. Ensure that KDC and Bob are running.
2. Select option 1 in Alice's terminal.
3. Enter the message to be sent.
4. Alice requests a Session Key from KDC.
5. Alice encrypts the message using AES-128 CBC.
6. Bob receives the encrypted message and ticket.
7. Bob decrypts the ticket and retrieves the Session Key.
8. Bob decrypts and displays the original message.

### Sending a Message from Bob to Alice

1. Ensure that KDC and Alice are running.
2. Select option 1 in Bob's terminal.
3. Enter the message to be sent.
4. Bob requests a Session Key from KDC.
5. Bob encrypts the message using AES-128 CBC.
6. Alice receives the encrypted message and ticket.
7. Alice decrypts the ticket and retrieves the Session Key.
8. Alice decrypts and displays the original message.

## 11. Expected Results

A successful communication should demonstrate:

- KDC successfully generates a random Session Key.
- Alice and Bob receive the appropriate encrypted key distribution response.
- Messages are encrypted before transmission.
- The recipient successfully decrypts the encrypted ticket.
- The recipient retrieves the Session Key.
- The original plaintext message is successfully recovered.

Example:

```text
--- MENU ALICE ---
1. Kirim Pesan ke Bob

Masukkan pesan ASCII untuk Bob:
Hello Bob, this is Alice!

[TERKIRIM] Ciphertext Hex: ...
```

On Bob's terminal:

```text
[PESAN MASUK dari Alice]:
Hello Bob, this is Alice!
```

## 12. Important Notes and Limitations

- Alice's and Bob's Master Keys must match the corresponding keys configured in KDC.
- Master Keys must contain exactly 16 ASCII characters for this configuration.
- The interactive Master Key change option in the current client code only changes the local client variable. It does not automatically update KDC.
- Ensure that the three devices can communicate over the network and that their firewall settings allow the required TCP connections.
- This project is intended for educational and practical laboratory purposes.

**Security Note:** The current implementation uses AES-CBC without message authentication. IV reuse across encryption operations and the absence of client authentication mean that this implementation should not be used for production security.

## 13. Conclusion

This project demonstrates the implementation of AES-128 encryption and decryption combined with a Key Distribution Center for symmetric key management.

Through the communication between Alice, Bob, and KDC, the project illustrates how Master Keys are used to distribute a randomly generated Session Key, allowing two parties to exchange encrypted messages.

The implementation provides practical experience in AES internals, CBC mode, key expansion, network socket programming, and symmetric cryptographic key distribution.

---

**Course:** Cryptography  
**Practical Assignment:** AES-128 and Key Distribution Center  
**Programming Language:** Python 3  
**Encryption Algorithm:** AES-128  
**Operation Mode:** CBC  
**Communication Protocol:** TCP/IP  
**Main Components:** Alice, Bob, and Key Distribution Center (KDC)

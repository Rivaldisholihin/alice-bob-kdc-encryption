# Implementasi AES-128 dan Key Distribution Center (KDC)

## 1. Deskripsi Proyek

Proyek ini merupakan implementasi sistem komunikasi menggunakan algoritma kriptografi simetris **AES-128 (Advanced Encryption Standard)** dengan bantuan **Key Distribution Center (KDC)**.

Sistem ini memungkinkan dua pihak, yaitu Alice dan Bob, untuk bertukar pesan terenkripsi dengan bantuan KDC sebagai pihak ketiga yang dipercaya (*Trusted Third Party*).

KDC bertugas menghasilkan Session Key secara acak dan mendistribusikannya kepada Alice dan Bob menggunakan Master Key masing-masing. Setelah memperoleh Session Key yang sama, Alice dan Bob dapat melakukan komunikasi menggunakan algoritma AES-128.

Implementasi ini menggunakan mode operasi **Cipher Block Chaining (CBC)** dengan algoritma AES-128 yang dibuat secara manual menggunakan bahasa pemrograman Python.

## 2. Tujuan Proyek

- Mengimplementasikan algoritma enkripsi dan dekripsi AES-128 secara manual.
- Memahami proses Key Expansion pada algoritma AES.
- Mengimplementasikan mode operasi Cipher Block Chaining (CBC).
- Membangun Key Distribution Center untuk menghasilkan dan mendistribusikan Session Key.
- Membangun komunikasi terenkripsi antara Alice dan Bob.
- Mendemonstrasikan komunikasi menggunakan tiga alamat IP yang berbeda.
- Memahami fungsi Master Key dan Session Key dalam kriptografi simetris.

## 3. Arsitektur Sistem

Sistem ini terdiri dari tiga entitas utama:

| Entitas | Fungsi | Port Default |
|---|---|---|
| KDC | Menghasilkan dan mendistribusikan Session Key | 5000 |
| Alice | Mengirim dan menerima pesan terenkripsi | 5001 |
| Bob | Mengirim dan menerima pesan terenkripsi | 5002 |

### Diagram Arsitektur Komunikasi

```text
              +----------------+
              |      KDC       |
              |   Port: 5000   |
              |                |
              | Session Key    |
              | Generation     |
              +----------------+
                  /       \
                 /         \
          Master Key    Master Key
               /             \
              /               \
     +---------------+  +---------------+
     |     ALICE     |  |      BOB      |
     |   Port: 5001  |  |   Port: 5002  |
     +---------------+  +---------------+
              \              /
               \            /
                Komunikasi
               AES-128 CBC
```

Setiap entitas dapat berperan sebagai pengirim maupun penerima pesan.

Arah komunikasi yang didukung:
- Alice → Bob
- Bob → Alice

## 4. Implementasi Kriptografi

### 4.1 Advanced Encryption Standard (AES-128)

AES-128 merupakan algoritma kriptografi simetris berbasis blok yang menggunakan:
- Ukuran blok: 128 bit (16 byte).
- Panjang kunci: 128 bit (16 byte).
- Jumlah putaran: 10 ronde.

Implementasi AES-128 dalam proyek ini mencakup beberapa tahapan:

1. SubBytes
2. ShiftRows
3. MixColumns
4. AddRoundKey
5. Key Expansion

Pada ronde terakhir, proses MixColumns tidak dilakukan.

### 4.2 Cipher Block Chaining (CBC)

Cipher Block Chaining (CBC) merupakan mode operasi yang digunakan untuk mengenkripsi data menggunakan algoritma AES.

Pada proses enkripsi, setiap blok plaintext akan di-XOR dengan blok ciphertext sebelumnya sebelum dienkripsi.

Blok pertama menggunakan Initialization Vector (IV).

Rumus enkripsi:

```text
C1 = AES(K, P1 XOR IV)

C2 = AES(K, P2 XOR C1)
```

Keterangan:
- K = Kunci enkripsi.
- P = Plaintext.
- C = Ciphertext.
- IV = Initialization Vector.

Implementasi ini juga menggunakan PKCS7 Padding untuk memastikan panjang plaintext sesuai dengan ukuran blok AES, yaitu 16 byte.

### 4.3 Distribusi Kunci

Sistem menggunakan dua jenis kunci kriptografi:

**Master Key**
- Alice dan KDC memiliki Master Key yang sama.
- Bob dan KDC memiliki Master Key yang sama.
- Digunakan untuk melindungi proses distribusi Session Key.

**Session Key**
- Dibuat secara acak oleh KDC.
- Digunakan Alice dan Bob untuk mengenkripsi serta mendekripsi pesan.
- Memiliki panjang 128 bit (16 byte).

## 5. Proses Distribusi Session Key

Proses komunikasi mengikuti tahapan berikut:

1. Alice mengirimkan permintaan Session Key kepada KDC untuk berkomunikasi dengan Bob.
2. KDC menghasilkan Session Key dan IV secara acak.
3. KDC membuat ticket yang berisi identitas pengirim, penerima, Session Key, dan IV.
4. Ticket dienkripsi menggunakan Master Key Bob.
5. KDC mengenkripsi Session Key dan ticket menggunakan Master Key Alice.
6. Alice mendekripsi respons KDC menggunakan Master Key miliknya.
7. Alice memperoleh Session Key dan ticket terenkripsi untuk Bob.
8. Alice mengenkripsi pesan menggunakan Session Key.
9. Alice mengirimkan pesan terenkripsi beserta ticket kepada Bob.
10. Bob mendekripsi ticket menggunakan Master Key miliknya.
11. Bob memperoleh Session Key dan menggunakannya untuk mendekripsi pesan Alice.

Proses yang sama berlaku ketika Bob ingin berkomunikasi dengan Alice.

## 6. Struktur Direktori Proyek

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

### Penjelasan File

| Nama File | Fungsi |
|---|---|
| `aes_manual.py` | Berisi implementasi manual algoritma AES-128, proses enkripsi, dekripsi, mode CBC, dan Key Expansion. |
| `kdc.py` | Mengimplementasikan Key Distribution Center untuk menghasilkan dan mendistribusikan Session Key. |
| `alice.py` | Mengimplementasikan program client Alice untuk meminta Session Key, mengenkripsi, dan mendekripsi pesan. |
| `bob.py` | Mengimplementasikan program client Bob untuk meminta Session Key, mengenkripsi, dan mendekripsi pesan. |
| `README.md` | Dokumentasi proyek dan panduan penggunaan program. |

## 7. Persyaratan Sistem

Sebelum menjalankan program, pastikan perangkat memenuhi persyaratan berikut:

- Python versi 3.x.
- Tiga komputer atau perangkat yang terhubung dalam satu jaringan.
- Koneksi jaringan antara Alice, Bob, dan KDC.
- Port TCP 5000, 5001, dan 5002 dapat diakses.
- Tidak memerlukan instalasi library Python tambahan karena menggunakan library bawaan Python.

## 8. Instalasi dan Konfigurasi

### Langkah 1: Persiapan File

Salin seluruh file Python ke direktori proyek pada masing-masing komputer.

### Langkah 2: Konfigurasi Alamat IP

Tugas praktikum ini mensyaratkan komunikasi menggunakan tiga alamat IP yang berbeda.

Contoh konfigurasi jaringan:

| Perangkat | Alamat IP | Port |
|---|---|---|
| KDC | 192.168.1.10 | 5000 |
| Alice | 192.168.1.11 | 5001 |
| Bob | 192.168.1.12 | 5002 |

Ganti alamat IP contoh tersebut sesuai dengan alamat IP aktual masing-masing perangkat.

### Langkah 3: Konfigurasi Environment Variables

**Pada komputer KDC:**

```powershell
$env:KDC_HOST="0.0.0.0"
$env:KDC_PORT="5000"
```

**Pada komputer Alice:**

```powershell
$env:KDC_HOST="192.168.1.10"
$env:KDC_PORT="5000"
$env:ALICE_HOST="0.0.0.0"
$env:ALICE_PORT="5001"
$env:BOB_HOST="192.168.1.12"
$env:BOB_PORT="5002"
```

**Pada komputer Bob:**

```powershell
$env:KDC_HOST="192.168.1.10"
$env:KDC_PORT="5000"
$env:BOB_HOST="0.0.0.0"
$env:BOB_PORT="5002"
$env:ALICE_HOST="192.168.1.11"
$env:ALICE_PORT="5001"
```

## 9. Menjalankan Program

Jalankan program dengan urutan berikut.

### Terminal 1 – KDC

```bash
python kdc.py
```

Output yang diharapkan:

```text
[KDC Server Ready] Listening on 0.0.0.0:5000
```

### Terminal 2 – Alice

```bash
python alice.py
```

Output yang diharapkan:

```text
[Alice Ready] Port: 5001

--- MENU ALICE ---
1. Kirim Pesan ke Bob
2. Ubah Master Key (Interaktif)
3. Keluar
```

### Terminal 3 – Bob

```bash
python bob.py
```

Output yang diharapkan:

```text
[Bob Ready] Port: 5002

--- MENU BOB ---
1. Kirim Pesan ke Alice
2. Ubah Master Key (Interaktif)
3. Keluar
```

## 10. Cara Penggunaan Program

### 10.1 Mengirim Pesan dari Alice ke Bob

1. Pastikan program KDC dan Bob sudah berjalan.
2. Pilih menu nomor 1 pada terminal Alice.
3. Masukkan pesan yang ingin dikirim.
4. Alice meminta Session Key kepada KDC.
5. Alice mengenkripsi pesan menggunakan AES-128 CBC.
6. Bob menerima pesan terenkripsi beserta ticket.
7. Bob mendekripsi ticket menggunakan Master Key miliknya.
8. Bob memperoleh Session Key.
9. Bob mendekripsi pesan dan menampilkan plaintext.

### 10.2 Mengirim Pesan dari Bob ke Alice

1. Pastikan program KDC dan Alice sudah berjalan.
2. Pilih menu nomor 1 pada terminal Bob.
3. Masukkan pesan yang ingin dikirim.
4. Bob meminta Session Key kepada KDC.
5. Bob mengenkripsi pesan menggunakan AES-128 CBC.
6. Alice menerima pesan terenkripsi beserta ticket.
7. Alice mendekripsi ticket menggunakan Master Key miliknya.
8. Alice memperoleh Session Key.
9. Alice mendekripsi pesan dan menampilkan plaintext.

## 11. Hasil yang Diharapkan

Komunikasi dinyatakan berhasil apabila:

- KDC berhasil menghasilkan Session Key secara acak.
- Alice dan Bob memperoleh respons distribusi kunci yang sesuai.
- Pesan dienkripsi sebelum dikirimkan.
- Penerima berhasil mendekripsi ticket.
- Penerima memperoleh Session Key.
- Pesan asli berhasil diperoleh kembali setelah proses dekripsi.

Contoh pengiriman pesan dari Alice:

```text
--- MENU ALICE ---
1. Kirim Pesan ke Bob

Masukkan pesan ASCII untuk Bob:
Hello Bob, this is Alice!

[TERKIRIM] Ciphertext Hex: ...
```

Contoh pesan yang diterima Bob:

```text
[PESAN MASUK dari Alice]:
Hello Bob, this is Alice!
```

## 12. Catatan dan Batasan Sistem

Beberapa hal yang perlu diperhatikan:

- Master Key Alice dan Bob harus sesuai dengan Master Key yang tersimpan pada KDC.
- Master Key harus terdiri dari tepat 16 karakter ASCII untuk konfigurasi ini.
- Fitur perubahan Master Key pada menu Alice dan Bob saat ini hanya mengubah variabel lokal client. Perubahan tersebut belum otomatis dikirimkan atau diperbarui pada KDC.
- Pastikan ketiga perangkat dapat saling berkomunikasi melalui jaringan.
- Pastikan pengaturan firewall mengizinkan koneksi TCP pada port yang digunakan.
- Program ini dikembangkan untuk kebutuhan pembelajaran dan praktikum kriptografi.

**Catatan Keamanan:** Implementasi saat ini menggunakan AES-CBC tanpa autentikasi integritas pesan. Penggunaan IV yang sama pada beberapa operasi enkripsi dan tidak adanya autentikasi client juga menjadi keterbatasan. Oleh karena itu, program ini ditujukan untuk demonstrasi akademik dan bukan untuk penggunaan keamanan produksi.

## 13. Kesimpulan

Proyek ini mendemonstrasikan implementasi algoritma AES-128 untuk proses enkripsi dan dekripsi pesan dengan memanfaatkan Key Distribution Center sebagai pengelola distribusi kunci simetris.

Melalui komunikasi antara Alice, Bob, dan KDC, proyek ini menunjukkan bagaimana Master Key digunakan untuk melindungi distribusi Session Key yang dihasilkan secara acak sehingga dua pihak dapat bertukar pesan terenkripsi.

Implementasi ini memberikan pemahaman praktis mengenai algoritma AES, mode operasi CBC, Key Expansion, pemrograman jaringan menggunakan Socket TCP, serta mekanisme distribusi kunci dalam kriptografi simetris.

---

**Mata Kuliah:** Kriptografi  
**Tugas:** Implementasi AES-128 dan Key Distribution Center  
**Bahasa Pemrograman:** Python 3  
**Algoritma Enkripsi:** AES-128  
**Mode Operasi:** CBC  
**Protokol Komunikasi:** TCP/IP  
**Komponen Utama:** Alice, Bob, dan Key Distribution Center (KDC)

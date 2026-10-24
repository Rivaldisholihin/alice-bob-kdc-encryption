# Tugas Network Security: Distribusi Kunci dengan KDC dan AES

## Arsitektur

- KDC membangkitkan session key AES-256.
- KDC membungkus session key untuk Alice menggunakan master key Alice.
- KDC membuat tiket untuk Bob yang dilindungi master key Bob.
- Alice membuka paket dari KDC, lalu mengirim tiket dan pesan terenkripsi ke Bob.
- Bob membuka tiket, memperoleh session key, lalu mendekripsi pesan.

Program memakai AES-GCM agar enkripsi juga memeriksa integritas dan keaslian ciphertext.

## 1. Persiapan

Pasang Python 3.10 atau lebih baru di ketiga komputer. Salin folder proyek ke setiap komputer, lalu jalankan:

```bash
python -m pip install -r requirements.txt
```

Buat dua kunci master berbeda, masing-masing 64 karakter heksadesimal (32 byte). Contoh untuk membuat kunci secara lokal:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Jalankan perintah tersebut dua kali. Simpan hasil pertama sebagai master key Alice dan hasil kedua sebagai master key Bob. Jangan memakai kunci contoh atau mengirim kunci master melalui jaringan.

## 2. Konfigurasi alamat IP

Ganti contoh alamat berikut dengan IP lokal yang benar dari masing-masing komputer:

- KDC: `192.168.1.10`
- Alice: `192.168.1.11`
- Bob: `192.168.1.12`

Ketiganya harus dapat saling terhubung melalui jaringan. Buka TCP port 5000 di komputer KDC dan TCP port 5002 di komputer Bob pada firewall.

## 3. Jalankan KDC

Pada komputer KDC, atur environment variable:

Windows PowerShell:

```powershell
$env:ALICE_MASTER_KEY="ISI_KUNCI_MASTER_ALICE"
$env:BOB_MASTER_KEY="ISI_KUNCI_MASTER_BOB"
$env:KDC_HOST="0.0.0.0"
$env:KDC_PORT="5000"
python kdc.py
```

Linux/macOS:

```bash
export ALICE_MASTER_KEY="ISI_KUNCI_MASTER_ALICE"
export BOB_MASTER_KEY="ISI_KUNCI_MASTER_BOB"
export KDC_HOST="0.0.0.0"
export KDC_PORT="5000"
python kdc.py
```

## 4. Jalankan Bob

Pada komputer Bob, gunakan master key Bob yang sama persis dengan yang disimpan di KDC.

Windows PowerShell:

```powershell
$env:BOB_MASTER_KEY="ISI_KUNCI_MASTER_BOB"
$env:BOB_HOST="0.0.0.0"
$env:BOB_PORT="5002"
python bob.py
```

Linux/macOS:

```bash
export BOB_MASTER_KEY="ISI_KUNCI_MASTER_BOB"
export BOB_HOST="0.0.0.0"
export BOB_PORT="5002"
python bob.py
```

## 5. Jalankan Alice

Pada komputer Alice, gunakan master key Alice yang sama persis dengan yang disimpan di KDC. Atur IP KDC dan Bob sesuai jaringan.

Windows PowerShell:

```powershell
$env:ALICE_MASTER_KEY="ISI_KUNCI_MASTER_ALICE"
$env:KDC_HOST="192.168.1.10"
$env:KDC_PORT="5000"
$env:BOB_HOST="192.168.1.12"
$env:BOB_PORT="5002"
python alice.py
```

Linux/macOS:

```bash
export ALICE_MASTER_KEY="ISI_KUNCI_MASTER_ALICE"
export KDC_HOST="192.168.1.10"
export KDC_PORT="5000"
export BOB_HOST="192.168.1.12"
export BOB_PORT="5002"
python alice.py
```

Masukkan pesan saat diminta. Bob akan menampilkan pesan yang berhasil didekripsi.

## Urutan demonstrasi

1. Alice meminta session key ke KDC.
2. KDC menghasilkan session key AES-256.
3. KDC mengirim session key dalam paket terenkripsi untuk Alice dan tiket terenkripsi untuk Bob.
4. Alice membuka paketnya dan mengirim tiket serta ciphertext pesan ke Bob.
5. Bob membuka tiket dengan master key Bob, mendapatkan session key, lalu mendekripsi pesan.

## Catatan keamanan dan batasan

- Gunakan tiga komputer atau tiga mesin virtual dengan tiga IP berbeda untuk memenuhi catatan tugas.
- Contoh ini untuk demonstrasi akademik di jaringan tepercaya. Belum mengimplementasikan autentikasi koneksi lengkap, pencegahan replay, masa berlaku tiket, atau transport TLS.
- AES-GCM menyediakan pemeriksaan integritas untuk paket yang dienkripsi, tetapi tidak menggantikan autentikasi jaringan dan manajemen kunci produksi.
- Kunci master disetel melalui environment variable agar tidak ditulis langsung dalam kode.

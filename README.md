# Wordle Kripto — RSA Edition

Permainan tebak kata 5 huruf (Wordle) berbasis kriptografi RSA untuk tugas projek kelompok **Matematika Diskrit 2 (Topik Kriptografi Bagian 4.6)**.

Kata rahasia tidak disimpan sebagai teks biasa, melainkan dienkripsi menjadi *ciphertext* RSA (**Sandi Misteri C**). Pemain melihat kunci publik $(n, e)$ dan sandi misteri $C$, lalu menebak kata aslinya dalam maksimal 6 percobaan. Seluruh algoritma inti RSA, uji primalitas, eksponensiasi modular cepat, dan sistem encoding angka ditulis dari dasar (**murni tanpa pustaka kriptografi pihak ketiga**).

---

## 🚀 Cara Menjalankan

### Persyaratan Sistem
- Python versi **3.8 atau lebih baru** (disarankan Python 3.10+).
- Tidak memerlukan instalasi paket tambahan (`pip install` tidak diperlukan). Seluruh dependensi merupakan pustaka standar bawaan Python.

### 1. Menjalankan Antarmuka Grafis / GUI (Default)
```bash
python main.py
```
*Membuka jendela GUI Tkinter lengkap dengan papan kotak 6×5, keyboard virtual terwarnai, panel kunci publik RSA, dialog verifikasi tanda tangan digital, serta menu Lab Kripto.*

### 2. Menjalankan Mode Terminal / CLI
```bash
python main.py --cli
```

### 3. Opsi Parameter Lanjutan
```bash
# Menjalankan dengan ukuran kunci acak (Miller-Rabin)
python main.py --cli --kunci kecil    # Prima ~16-bit
python main.py --cli --kunci sedang   # Prima ~24-bit
python main.py --cli --kunci besar    # Prima ~32-bit

# Menggunakan seed acak tertentu (reproduktif untuk demo/pengujian)
python main.py --cli --seed 42

# Menjalankan dengan kunci manual
python main.py --cli --p 51001 --q 51031 --e 65537

# Menjalankan seluruh pengujian unit otomatis
python -m unittest discover tests/ -v
```

---

## 📁 Struktur Direktori Projek

```text
projek/
├── main.py                     # Titik masuk program (launcher GUI dan mode CLI)
├── gui.py                      # Antarmuka grafis (Tkinter) interaktif (P1)
├── game_master.py              # Pengelola rahasia (enkapsulasi d, C, dan tanda tangan digital)
├── wordle_engine.py            # Logika aturan Wordle dan algoritma evaluasi warna dua tahap
├── rsa_core.py                 # Algoritma RSA murni (Euclid, invers modulo, kuadrat-dan-kali, Miller-Rabin)
├── encoding.py                 # Konversi teks A-Z ke angka 2 digit dan kalkulasi ukuran blok
├── lab_kripto.py               # Lab Kripto P2: enkripsi multi-blok, serangan kamus, faktorisasi n
├── kata.txt                    # Kamus kata 5 huruf kapital bahasa Inggris (5.700+ kata)
├── RSA.py                      # File kode rintisan awal sebelum refaktor
├── PRD — Wordle Kripto.md      # Dokumen Product Requirement Document (PRD v0.2)
├── tests/                      # Suite pengujian unit otomatis (100% lulus)
│   ├── __init__.py
│   ├── test_rsa_core.py        # Pengujian algoritma kriptografi & data slide dosen
│   ├── test_encoding.py        # Pengujian encoding alfabet & pembagian blok
│   └── test_wordle_engine.py   # Pengujian aturan Wordle & huruf kembar
└── skeletons/                  # Template / Skeleton pengerjaan mandiri bagi anggota tim
    ├── rsa_core_skeleton.py    # Template algoritma RSA dengan petunjuk rumus
    └── encoding_skeleton.py    # Template encoding dengan petunjuk blok
```

---

## 📚 Kebijakan dan Daftar Library

Sesuai ketentuan dosen dan PRD Bagian 9, **seluruh algoritma kriptografi RSA ditulis sendiri tanpa pustaka pihak ketiga**. Tidak ada pustaka seperti `pycryptodome`, `rsa`, `cryptography`, `sympy`, maupun `gmpy2`. Fungsi bawaan seperti `math.gcd` atau `pow(a, b, m)` 3-argumen **tidak digunakan** di dalam kode program inti (hanya dipakai sebagai verifikator pembanding di file uji unit `tests/`).

| Nama Pustaka | Lokasi Penggunaan | Alasan & Peran |
| :--- | :--- | :--- |
| `random` | `rsa_core.py`, `game_master.py` | Pemilihan kandidat prima acak dan pengacakan kata rahasia. |
| `secrets` | `rsa_core.py` | Alternatif CSPRNG standar Python. |
| `tkinter`, `ttk` | `gui.py`, `lab_kripto.py` | Pembuatan antarmuka visual desktop bawaan Python. |
| `time` | `lab_kripto.py` | Pengukuran durasi komputasi faktorisasi dan serangan kamus. |
| `argparse` | `main.py` | Penanganan argumen baris perintah CLI. |
| `os`, `sys` | `main.py`, `game_master.py` | Penanganan file I/O dan path direktori. |
| `unittest` | `tests/` | Framework otomasi pengujian unit bawaan Python. |

---

## 🔬 Teori dan Rumus Aritmetika Modular

### 1. Representasi Numerik (Encoding)
- Alfabet $A = 00, B = 01, C = 02, \dots, Z = 25$.
- Setiap huruf dinyatakan dalam 2 digit angka.
- Kata 5 huruf menjadi string 10 digit angka:
  $$\text{BUNGA} \implies B(01)\;U(20)\;N(13)\;G(06)\;A(00) \implies M = 0120130600$$

### 2. Penentuan Ukuran Blok $2N$ Digit
Blok terdiri dari $2N$ digit (bilangan genap terbesar) sehingga bilangan $2525\dots 25$ ($2N$ digit) tidak melebihi modulus $n$ ($2525\dots 25 \le n$).
- Pada $n = 2537$: $2525 \le 2537 < 252525 \implies$ blok 4 digit (2 huruf).
- Pada mode game ($n \ge 2.525.252.525$): blok 10 digit (muat tepat 5 huruf).

### 3. Pembuatan Pasangan Kunci RSA
1. Pilih dua bilangan prima $p$ dan $q$ ($p \ne q$).
2. Hitung modulus: $n = p \times q$.
3. Hitung fungsi Totient Euler: $\phi(n) = (p - 1)(q - 1)$.
4. Pilih eksponen publik $e$ sedemikian sehingga $1 < e < \phi(n)$ dan $\gcd(e, \phi(n)) = 1$ (diperiksa dengan Algoritma Euclid).
5. Hitung eksponen privat $d$ sebagai invers perkalian modular:
   $$e \cdot d \equiv 1 \pmod{\phi(n)}$$
   dihitung menggunakan **Algoritma Euclid yang Diperluas (Extended Euclidean Algorithm)**.

### 4. Enkripsi dan Dekripsi
- **Enkripsi**: $C = M^e \pmod n$
- **Dekripsi**: $M = C^d \pmod n$
- Dihitung efisien menggunakan metode **Kuadrat-dan-Kali (Square-and-Multiply)** dengan reduksi modulo di setiap perkalian.

### 5. Tanda Tangan Digital (F-12)
- Penandatanganan ringkasan hasil $R$: $S = R^{d_{\text{sign}}} \pmod{n_{\text{sign}}}$
- Verifikasi tanda tangan: $S^{e_{\text{sign}}} \pmod{n_{\text{sign}}} \stackrel{?}{=} R$
- Pasangan kunci tanda tangan dibuat **terpisah** dari kunci game agar keamanan sandi misteri tetap terlindungi.

---

## 🧪 Verifikasi Data Uji Materi Dosen

Program telah diuji dan terbukti valid terhadap seluruh data uji dari slide kuliah:
1. **Contoh Slide Kuliah ($p=43, q=59, n=2537, e=13, d=937$):**
   - Enkripsi kata `STOP` (blok `1819` dan `1415`) $\implies C_1 = 2081$ dan $C_2 = 2182$.
   - Dekripsi cipher `0981` dan `0461` $\implies M_1 = 0704$ (`HE`) dan $M_2 = 1115$ (`LP`) $\implies$ `HELP`.
   - Tanda tangan digital `MEET AT NOON` $\implies$ blok $[1204, 0419, 0019, 1314, 1413] \implies [0817, 0555, 1310, 2173, 1026]$ dan terverifikasi valid.
2. **Parameter Default Permainan ($p=51001, q=51031, e=65537$):**
   - $n = 2602632031$, $\phi = 2602530000$, $d = 154713473$.
   - Kata `BUNGA` ($M = 0120130600$) $\implies C = 587403072 \implies$ didekripsi kembali menjadi `BUNGA`.
   - Kata `BUKAN` $\implies C = 293955741$.
   - Kata ekstrem `ZZZZZ` ($M = 2525252525$) $\implies$ berhasil dienkripsi dan didekripsi utuh.

---

## 👥 Tabel Kontribusi Anggota Kelompok

Tabel ini disiapkan untuk dipindahkan ke Bab 5 makalah:

| No | Nama Anggota | NIM | Bagian Kode | Bagian Makalah |
|:--:|:---|:---:|:---|:---|
| 1 | *(Nama Anggota 1)* | *(NIM)* | `rsa_core.py`, `encoding.py`, `tests/` | Bab 2 (Landasan Teori Aritmetika Modular) |
| 2 | *(Nama Anggota 2)* | *(NIM)* | `wordle_engine.py`, `game_master.py` | Bab 3 (Rancangan & Arsitektur Program) |
| 3 | *(Nama Anggota 3)* | *(NIM)* | `gui.py`, `main.py` | Bab 4 (Antarmuka & Pengujian Sistem) |
| 4 | *(Nama Anggota 4)* | *(NIM)* | `lab_kripto.py`, `README.md`, `kata.txt` | Bab 1 (Pendahuluan) & Bab 6 (Penutup) |

"""
Modul rsa_core.py — Wordle Kripto (RSA Edition)

Mengimplementasikan seluruh algoritma inti kriptografi RSA dari dasar tanpa
menggunakan pustaka pihak ketiga maupun fungsi bawaan seperti math.gcd atau
pow 3-argumen.

Rumus Matematika & Konsep Utama:
1. n = p * q, φ(n) = (p - 1) * (q - 1)
2. Kunci publik: (n, e) di mana 1 < e < φ(n) dan FPB(e, φ(n)) = 1
3. Kunci privat: (n, d) di mana e * d ≡ 1 (mod φ(n)), dicari dengan Algoritma Euclid Diperluas
4. Enkripsi: C = M^e mod n (menggunakan kuadrat-dan-kali)
5. Dekripsi: M = C^d mod n (menggunakan kuadrat-dan-kali)
6. Tanda tangan digital: S = R^d mod n, Verifikasi: S^e mod n == R
"""

import random
import secrets


def fpb(a: int, b: int) -> int:
    """
    Menghitung Faktor Persekutuan Terbesar (FPB) dari dua bilangan bulat a dan b
    menggunakan Algoritma Euclid.

    Algoritma Euclid berlandaskan sifat:
        FPB(a, b) = FPB(b, a mod b), untuk b ≠ 0
        FPB(a, 0) = |a|

    Parameters
    ----------
    a : int
        Bilangan bulat pertama.
    b : int
        Bilangan bulat kedua.

    Returns
    -------
    int
        FPB positif dari a dan b.
    """
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def euclid_diperluas(a: int, b: int) -> tuple:
    """
    Algoritma Euclid yang Diperluas (Extended Euclidean Algorithm).

    Menemukan FPB(a, b) beserta koefisien Bezout x dan y sedemikian hingga:
        a * x + b * y = FPB(a, b)

    Algoritma ini menjadi fondasi pencarian invers perkalian modular:
    Jika a * x + b * y = 1, maka:
        a * x ≡ 1 (mod b)
    Artinya x adalah invers dari a modulo b.

    Parameters
    ----------
    a : int
        Bilangan pertama (misalnya eksponen publik e).
    b : int
        Bilangan kedua (misalnya nilai totient Euler φ(n)).

    Returns
    -------
    tuple[int, int, int]
        (gcd, x, y) yang memenuhi a * x + b * y = gcd.
    """
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = euclid_diperluas(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def cari_d(e: int, phi: int) -> int:
    """
    Mencari kunci privat d sebagai invers perkalian dari e modulo φ(n).

    Persamaan kongruensi:
        e * d ≡ 1 (mod φ)

    Dengan Algoritma Euclid Diperluas, kita peroleh koefisien x sehingga:
        e * x + φ * y = 1
        e * x ≡ 1 (mod φ)
    Sehingga d = x mod φ (dipastikan bernilai positif antara 1 dan φ - 1).

    Parameters
    ----------
    e : int
        Eksponen publik.
    phi : int
        Nilai totient Euler φ(n) = (p - 1) * (q - 1).

    Returns
    -------
    int
        Eksponen privat d.

    Raises
    ------
    ValueError
        Jika e dan φ tidak relatif prima (gcd ≠ 1).
    """
    gcd, x, _ = euclid_diperluas(e, phi)
    if gcd != 1:
        raise ValueError("e dan φ tidak koprima (gcd ≠ 1), invers modulo tidak ada.")
    return (x % phi + phi) % phi


def eksponen_modular(basis: int, eksponen: int, modulus: int) -> int:
    """
    Menghitung (basis^eksponen) mod modulus secara efisien menggunakan
    algoritma Kuadrat-dan-Kali (Square-and-Multiply / Binary Exponentiation).

    Kompleksitas O(log(eksponen)) perkalian modular.
    Di setiap iterasi, nilai selalu direduksi modulo m agar tidak terjadi
    pembengkakan bilangan (overflow memori).

    Langkah Algoritma:
    1. Inisialisasi hasil = 1, basis = basis mod modulus.
    2. Periksa bit paling kanan (LSB) eksponen:
       - Jika bit bernilai 1 (eksponen ganjil), hasil = (hasil * basis) mod modulus.
    3. Geser eksponen ke kanan (eksponen = eksponen // 2).
    4. Kuadratkan basis: basis = (basis * basis) mod modulus.
    5. Ulangi sampai eksponen habis (0).

    Parameters
    ----------
    basis : int
        Bilangan pokok M atau C.
    eksponen : int
        Pangkat e atau d.
    modulus : int
        Modulus n.

    Returns
    -------
    int
        (basis^eksponen) mod modulus.
    """
    if modulus == 1:
        return 0
    if eksponen < 0:
        raise ValueError("Eksponen tidak boleh negatif dalam aritmetika modular ini.")

    hasil = 1
    basis = basis % modulus

    while eksponen > 0:
        if eksponen % 2 == 1:
            hasil = (hasil * basis) % modulus
        eksponen //= 2
        basis = (basis * basis) % modulus

    return hasil


def cek_prima_percobaan(n: int) -> bool:
    """
    Uji primalitas menggunakan Pembagian Percobaan (Trial Division).
    Efisien dan deterministik untuk bilangan kecil (n < 1.000.000).

    Langkah:
    1. Jika n <= 1: bukan prima.
    2. Jika n == 2 atau n == 3: prima.
    3. Jika n genap atau habis dibagi 3: bukan prima.
    4. Uji pembagi ganjil bentuk 6k ± 1 hingga batas √n.

    Parameters
    ----------
    n : int
        Bilangan yang akan diuji.

    Returns
    -------
    bool
        True jika prima, False jika komposit.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    limit = int(n**0.5) + 1
    i = 5
    while i <= limit:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True


def miller_rabin(n: int, k: int = 20) -> bool:
    """
    Uji primalitas probabilistik Miller-Rabin dengan k putaran saksi.

    Berdasarkan Teorema Kecil Fermat:
    Jika n prima dan a tidak membagi n, maka a^(n-1) ≡ 1 (mod n).
    Tulis n - 1 = 2^r * d dengan d ganjil.
    Jika n prima, maka untuk setiap saksi a:
        a^d ≡ 1 (mod n)  ATAU
        a^(2^s * d) ≡ -1 ≡ n - 1 (mod n) untuk suatu 0 ≤ s < r.

    Jika syarat di atas gagal untuk suatu a, maka n dipastikan komposit.
    Peluang komposit lolos k putaran adalah ≤ (1/4)^k (untuk k=20, < 10^-12).

    Parameters
    ----------
    n : int
        Bilangan yang diuji.
    k : int, optional
        Jumlah saksi acak (default=20).

    Returns
    -------
    bool
        True jika kemungkinan besar prima, False jika komposit.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Faktorkan n - 1 menjadi 2^r * d
    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Uji dengan k saksi acak
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = eksponen_modular(a, d, n)
        if x == 1 or x == n - 1:
            continue

        komposit = True
        for _ in range(r - 1):
            x = eksponen_modular(x, 2, n)
            if x == n - 1:
                komposit = False
                break

        if komposit:
            return False

    return True


def cek_prima(n: int) -> bool:
    """
    Dispatcher uji primalitas cerdas:
    - n < 1.000.000: Menggunakan pembagian percobaan deterministik cepat.
    - n >= 1.000.000: Menggunakan uji probabilistik Miller-Rabin.

    Parameters
    ----------
    n : int
        Bilangan yang akan diuji.

    Returns
    -------
    bool
        True jika prima, False jika bukan.
    """
    if n < 1_000_000:
        return cek_prima_percobaan(n)
    return miller_rabin(n, k=25)


def buat_prima_acak(bits: int, seed: int = None) -> int:
    """
    Menghasilkan bilangan prima acak dengan ukuran tepat 'bits' bit.

    Menjamin bit tertinggi (MSB) dan bit terendah (LSB) bernilai 1
    sehingga bilangan berukuran tepat 'bits' bit dan ganjil.

    Parameters
    ----------
    bits : int
        Jumlah bit (misal: 16, 24, 32).
    seed : int, optional
        Seed pengacakan untuk pengujian reproduktif.

    Returns
    -------
    int
        Bilangan prima acak.
    """
    if seed is not None:
        random.seed(seed)

    while True:
        # Hasilkan bilangan ganjil bits-bit dengan MSB=1
        kandidat = (1 << (bits - 1)) | random.getrandbits(bits - 2) << 1 | 1
        if cek_prima(kandidat):
            return kandidat


def buat_kunci(p: int, q: int, e: int, mode_game: bool = True) -> tuple:
    """
    Memvalidasi parameter p, q, e dan menghitung kunci RSA (n, e, d).

    Validasi Lengkap:
    1. p ≠ q
    2. p dan q keduanya prima
    3. 1 < e < φ(n)
    4. FPB(e, φ(n)) = 1 (e dan φ relatif prima)
    5. Pada mode game: n ≥ 2.525.252.525 (agar kata 5 huruf / 10 digit muat 1 blok)

    Parameters
    ----------
    p : int
        Bilangan prima pertama.
    q : int
        Bilangan prima kedua.
    e : int
        Eksponen publik.
    mode_game : bool, optional
        Jika True, menerapkan syarat n ≥ 2525252525. Default True.

    Returns
    -------
    tuple[int, int, int]
        (n, e, d) di mana (n, e) kunci publik dan (n, d) kunci privat.

    Raises
    ------
    ValueError
        Dengan penjelasan spesifik jika ada syarat yang dilanggar.
    """
    if p == q:
        raise ValueError("Nilai p dan q tidak boleh sama.")

    if not cek_prima(p):
        raise ValueError(f"p ({p}) bukan bilangan prima, tolong ubah angka p.")

    if not cek_prima(q):
        raise ValueError(f"q ({q}) bukan bilangan prima, tolong ubah angka q.")

    n = p * q
    phi = (p - 1) * (q - 1)

    if e <= 1 or e >= phi:
        raise ValueError(f"e ({e}) harus berada dalam rentang 1 < e < φ ({phi}).")

    if fpb(e, phi) != 1:
        raise ValueError(f"gcd(e, φ) harus 1; FPB({e}, {phi}) = {fpb(e, phi)}. Pilih nilai e yang berbeda.")

    if mode_game and n < 2_525_252_525:
        raise ValueError(
            f"n ({n}) terlalu kecil untuk mode game (n harus ≥ 2525252525 agar kata 5 huruf muat dalam satu blok)."
        )

    d = cari_d(e, phi)
    return n, e, d


def buat_kunci_acak(ukuran: str = 'kecil', seed: int = None) -> tuple:
    """
    Menghasilkan pasangan kunci RSA acak yang valid untuk mode game Wordle Kripto.

    Ukuran Kunci yang Didukung:
    - 'kecil'  : prima ~16-17 bit (p, q sekitar 51000 - 65500, n ≥ 2.525.252.525)
    - 'sedang' : prima ~24 bit (p, q sekitar 1,6 x 10^7, n ~ 2,8 x 10^14)
    - 'besar'  : prima ~32 bit (p, q sekitar 4 x 10^9, n ~ 1,8 x 10^19)

    Parameters
    ----------
    ukuran : str
        'kecil', 'sedang', atau 'besar'.
    seed : int, optional
        Seed pengacakan.

    Returns
    -------
    tuple[int, int, int]
        (n, e, d)
    """
    bit_map = {
        'kecil': 16,
        'sedang': 24,
        'besar': 32,
    }
    bits = bit_map.get(ukuran.lower(), 16)
    e = 65537

    if seed is not None:
        random.seed(seed)

    while True:
        # Untuk ukuran 'kecil', pastikan p dan q cukup besar agar p * q >= 2525252525
        # sqrt(2525252525) ≈ 50251.9, jadi prima harus > 50252
        if bits == 16:
            p = buat_prima_acak(bits)
            while p < 50500:
                p = buat_prima_acak(bits)
            q = buat_prima_acak(bits)
            while q < 50500 or q == p:
                q = buat_prima_acak(bits)
        else:
            p = buat_prima_acak(bits)
            q = buat_prima_acak(bits)
            while q == p:
                q = buat_prima_acak(bits)

        n = p * q
        if n < 2_525_252_525:
            continue

        phi = (p - 1) * (q - 1)
        if e >= phi:
            # Gunakan e kecil yang koprima jika phi <= 65537
            e_kandidat = 3
            while fpb(e_kandidat, phi) != 1 or e_kandidat >= phi:
                e_kandidat += 2
            e_pilihan = e_kandidat
        else:
            if fpb(e, phi) != 1:
                continue
            e_pilihan = e

        try:
            d = cari_d(e_pilihan, phi)
            return n, e_pilihan, d
        except ValueError:
            continue


def enkripsi_blok(M: int, e: int, n: int) -> int:
    """
    Enkripsi satu blok pesan M menggunakan kunci publik (n, e).

    Rumus RSA:
        C = M^e mod n

    Parameters
    ----------
    M : int
        Plaintext berupa integer (harus 0 ≤ M < n).
    e : int
        Eksponen publik.
    n : int
        Modulus RSA.

    Returns
    -------
    int
        Ciphertext C.
    """
    if M < 0 or M >= n:
        raise ValueError(f"Nilai blok M ({M}) harus berada dalam rentang 0 ≤ M < n ({n}).")
    return eksponen_modular(M, e, n)


def dekripsi_blok(C: int, d: int, n: int) -> int:
    """
    Dekripsi satu blok ciphertext C menggunakan kunci privat (n, d).

    Rumus RSA:
        M = C^d mod n

    Parameters
    ----------
    C : int
        Ciphertext berupa integer (0 ≤ C < n).
    d : int
        Eksponen privat.
    n : int
        Modulus RSA.

    Returns
    -------
    int
        Plaintext M.
    """
    if C < 0 or C >= n:
        raise ValueError(f"Nilai ciphertext C ({C}) harus berada dalam rentang 0 ≤ C < n ({n}).")
    return eksponen_modular(C, d, n)


def tanda_tangan(R: int, d: int, n: int) -> int:
    """
    Menandatangani ringkasan data R menggunakan kunci privat penerbit (d, n).

    Protokol Tanda Tangan Digital RSA:
        S = R^d mod n

    Hanya pemilik kunci privat d yang dapat menghasilkan S yang valid.

    Parameters
    ----------
    R : int
        Ringkasan pesan / data berupa integer (0 ≤ R < n).
    d : int
        Kunci privat penanda tangan.
    n : int
        Modulus penanda tangan.

    Returns
    -------
    int
        Tanda tangan digital S.
    """
    if R < 0 or R >= n:
        raise ValueError(f"Nilai ringkasan R ({R}) harus berada dalam rentang 0 ≤ R < n ({n}).")
    return eksponen_modular(R, d, n)


def verifikasi_tanda_tangan(S: int, e: int, n: int, R_asli: int) -> bool:
    """
    Memverifikasi keaslian tanda tangan digital S menggunakan kunci publik (e, n).

    Verifikasi:
        S^e mod n == R_asli

    Jika data R atau tanda tangan S dimanipulasi sekecil apa pun,
    hasil eksponensiasi modular tidak akan cocok dengan R_asli.

    Parameters
    ----------
    S : int
        Tanda tangan digital.
    e : int
        Kunci publik penanda tangan.
    n : int
        Modulus penanda tangan.
    R_asli : int
        Nilai ringkasan data asli.

    Returns
    -------
    bool
        True jika tanda tangan valid, False jika palsu/rusak.
    """
    if S < 0 or S >= n:
        return False
    r_hitung = eksponen_modular(S, e, n)
    return r_hitung == R_asli

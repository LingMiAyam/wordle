"""
Modul encoding.py — Wordle Kripto (RSA Edition)

Mengatur konversi antara karakter teks alfabet dengan representasi numerik,
pembagian blok sesuai batas ukuran modulus n, serta enkripsi/dekripsi teks
berdasarkan materi kuliah Matematika Diskrit 2.

Aturan Pemetaan Alfabet:
    A = 00, B = 01, C = 02, ..., Z = 25
    Setiap huruf tepat diwakili oleh 2 digit angka.
    Kata 5 huruf menjadi string 10 digit angka.

Contoh:
    BUNGA -> B=01, U=20, N=13, G=06, A=00 -> "0120130600"
    STOP  -> S=18, T=19, O=14, P=15 -> "18191415"
"""

from rsa_core import enkripsi_blok, dekripsi_blok

ALFABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HURUF_KE_KODE = {huruf: f"{idx:02d}" for idx, huruf in enumerate(ALFABET)}
KODE_KE_HURUF = {f"{idx:02d}": huruf for idx, huruf in enumerate(ALFABET)}


def huruf_ke_angka(huruf: str) -> str:
    """
    Mengonversi satu huruf kapital (A-Z) menjadi string 2 digit (00-25).

    Parameters
    ----------
    huruf : str
        Satu karakter huruf kapital A-Z.

    Returns
    -------
    str
        Dua digit representasi angka (misal 'A' -> '00', 'Z' -> '25').

    Raises
    ------
    ValueError
        Jika input bukan huruf kapital tunggal A-Z.
    """
    if len(huruf) != 1 or huruf not in HURUF_KE_KODE:
        raise ValueError(f"Input harus satu huruf kapital A-Z, diterima: '{huruf}'.")
    return HURUF_KE_KODE[huruf]


def angka_ke_huruf(dua_digit: str) -> str:
    """
    Mengonversi string 2 digit angka (00-25) menjadi satu karakter huruf kapital.

    Parameters
    ----------
    dua_digit : str
        String 2 digit (misal '00' -> 'A', '25' -> 'Z').

    Returns
    -------
    str
        Karakter huruf kapital A-Z.

    Raises
    ------
    ValueError
        Jika input bukan 2 digit yang valid antara 00-25.
    """
    if len(dua_digit) != 2 or dua_digit not in KODE_KE_HURUF:
        raise ValueError(f"Input harus 2 digit antara 00-25, diterima: '{dua_digit}'.")
    return KODE_KE_HURUF[dua_digit]


def teks_ke_angka_str(teks: str) -> str:
    """
    Mengonversi seluruh string teks menjadi rangkaian string digit angka.
    Setiap huruf menjadi 2 digit berurutan.

    Parameters
    ----------
    teks : str
        String teks hanya berisi huruf A-Z kapital.

    Returns
    -------
    str
        String digit angka gabungan.

    Raises
    ------
    ValueError
        Jika teks mengandung karakter selain huruf A-Z.
    """
    teks_bersih = teks.strip().upper()
    hasil = []
    for char in teks_bersih:
        if char not in HURUF_KE_KODE:
            raise ValueError(f"Karakter '{char}' tidak valid; hanya huruf A-Z yang diizinkan.")
        hasil.append(HURUF_KE_KODE[char])
    return "".join(hasil)


def angka_str_ke_teks(s: str) -> str:
    """
    Mengonversi string digit angka kembali menjadi teks huruf kapital.
    String diproses berpasangan (per 2 digit).

    Parameters
    ----------
    s : str
        String digit angka dengan panjang genap.

    Returns
    -------
    str
        Teks huruf kapital hasil konversi.

    Raises
    ------
    ValueError
        Jika panjang string tidak genap atau pasangan digit tidak valid.
    """
    if len(s) % 2 != 0:
        raise ValueError(f"Panjang string digit harus genap, diterima panjang {len(s)}.")

    huruf_list = []
    for i in range(0, len(s), 2):
        pasangan = s[i : i + 2]
        huruf_list.append(angka_ke_huruf(pasangan))
    return "".join(huruf_list)


def hitung_ukuran_blok(n: int) -> int:
    """
    Menghitung ukuran blok digit (2N) berdasarkan modulus RSA n.

    Sesuai materi kuliah:
    Blok terdiri dari 2N digit, di mana 2N adalah bilangan genap terbesar
    sehingga bilangan 2525...25 (2N digit) tidak melebihi n (2525...25 ≤ n).
    Dengan aturan ini, nilai integer setiap blok M dipastikan selalu < n.

    Contoh:
    - n = 2537: 2525 ≤ 2537 < 252525 -> ukuran blok = 4 digit (2 huruf).
    - n = 2602632031: 2525252525 ≤ n < 252525252525 -> ukuran blok = 10 digit (5 huruf).

    Parameters
    ----------
    n : int
        Modulus RSA.

    Returns
    -------
    int
        Jumlah digit per blok (selalu bilangan genap).
    """
    if n < 25:
        raise ValueError(f"Modulus n ({n}) terlalu kecil untuk encoding blok.")

    N = 1
    while int("25" * (N + 1)) <= n:
        N += 1

    return 2 * N


def bagi_blok(s: str, ukuran_blok: int, pad_char: str = "0") -> list:
    """
    Membagi string digit menjadi daftar bilangan bulat blok berukuran `ukuran_blok` digit.
    Jika blok terakhir kurang dari `ukuran_blok`, ditambahkan padding di kanan.

    Parameters
    ----------
    s : str
        String digit angka.
    ukuran_blok : int
        Jumlah digit per blok.
    pad_char : str, optional
        Karakter padding jika blok terakhir kurang panjang (default '0').

    Returns
    -------
    list[int]
        Daftar nilai integer tiap blok.
    """
    if ukuran_blok <= 0 or ukuran_blok % 2 != 0:
        raise ValueError(f"Ukuran blok harus bilangan genap positif, diterima: {ukuran_blok}.")

    # Padding jika panjang tidak habis dibagi ukuran_blok
    sisa = len(s) % ukuran_blok
    if sisa != 0:
        s = s + pad_char * (ukuran_blok - sisa)

    blok_list = []
    for i in range(0, len(s), ukuran_blok):
        potongan = s[i : i + ukuran_blok]
        blok_list.append(int(potongan))

    return blok_list


def gabung_blok(list_int: list, ukuran_blok: int) -> str:
    """
    Menggabungkan daftar integer blok menjadi satu string digit angka utuh.
    Setiap integer di-format menjadi string dengan zero-padding di kiri
    sepanjang `ukuran_blok`.

    Parameters
    ----------
    list_int : list[int]
        Daftar integer blok.
    ukuran_blok : int
        Panjang digit per blok.

    Returns
    -------
    str
        String digit gabungan.
    """
    return "".join(str(val).zfill(ukuran_blok) for val in list_int)


def enkripsi_teks(teks: str, e: int, n: int) -> list:
    """
    Pipeline lengkap enkripsi teks bebas menjadi daftar ciphertext blok.

    Langkah:
    1. Teks -> string angka (2 digit per huruf).
    2. Hitung ukuran blok 2N dari n.
    3. Pecah string angka ke dalam blok integer.
    4. Enkripsi tiap blok: C = M^e mod n.

    Parameters
    ----------
    teks : str
        Teks pesan (A-Z).
    e : int
        Eksponen publik.
    n : int
        Modulus RSA.

    Returns
    -------
    list[int]
        Daftar ciphertext blok.
    """
    angka_str = teks_ke_angka_str(teks)
    ukuran_blok = hitung_ukuran_blok(n)
    blok_plain = bagi_blok(angka_str, ukuran_blok)
    return [enkripsi_blok(M, e, n) for M in blok_plain]


def dekripsi_teks(list_cipher: list, d: int, n: int, panjang_asli: int = None) -> str:
    """
    Pipeline lengkap dekripsi daftar ciphertext blok menjadi teks asli.

    Langkah:
    1. Dekripsi tiap blok: M = C^d mod n.
    2. Gabungkan blok integer menjadi string digit dengan zero-padding kiri.
    3. Jika panjang_asli diberikan, potong ke 2 * panjang_asli digit.
    4. Konversi string angka kembali ke teks.

    Parameters
    ----------
    list_cipher : list[int]
        Daftar ciphertext blok.
    d : int
        Eksponen privat.
    n : int
        Modulus RSA.
    panjang_asli : int, optional
        Jumlah karakter huruf asli (untuk membuang padding jika ada).

    Returns
    -------
    str
        Teks hasil dekripsi.
    """
    ukuran_blok = hitung_ukuran_blok(n)
    blok_plain = [dekripsi_blok(C, d, n) for C in list_cipher]
    angka_str = gabung_blok(blok_plain, ukuran_blok)

    if panjang_asli is not None:
        angka_str = angka_str[: panjang_asli * 2]

    return angka_str_ke_teks(angka_str)


def enkripsi_kata_game(kata: str, e: int, n: int) -> int:
    """
    Khusus mode Wordle Kripto: mengenkripsi satu kata 5 huruf (10 digit)
    menjadi satu bilangan integer ciphertext C.

    Syarat: n harus ≥ 2.525.252.525 agar kata seperti 'ZZZZZ' (M = 2525252525) < n.

    Parameters
    ----------
    kata : str
        Kata 5 huruf kapital A-Z.
    e : int
        Eksponen publik.
    n : int
        Modulus RSA.

    Returns
    -------
    int
        Ciphertext C tunggal.
    """
    kata = kata.strip().upper()
    if len(kata) != 5:
        raise ValueError(f"Kata game harus tepat 5 huruf, diterima '{kata}' ({len(kata)} huruf).")

    angka_str = teks_ke_angka_str(kata)
    M = int(angka_str)

    if M >= n:
        raise ValueError(
            f"Nilai M ({M}) melampaui modulus n ({n}). Ukuran kunci n tidak mencukupi untuk kata 5 huruf."
        )

    return enkripsi_blok(M, e, n)


def dekripsi_kata_game(C: int, d: int, n: int) -> str:
    """
    Khusus mode Wordle Kripto: mendekripsi satu bilangan integer ciphertext C
    menjadi kata 5 huruf kapital aslinya.

    Kritis: Nilai M integer didekripsi, kemudian di-zero-pad di kiri hingga tepat
    10 digit string sebelum didecode menjadi 5 huruf (misal untuk huruf awal A, B, C).

    Parameters
    ----------
    C : int
        Ciphertext integer.
    d : int
        Eksponen privat.
    n : int
        Modulus RSA.

    Returns
    -------
    str
        Kata 5 huruf hasil dekripsi.
    """
    M = dekripsi_blok(C, d, n)
    angka_str = str(M).zfill(10)
    return angka_str_ke_teks(angka_str)

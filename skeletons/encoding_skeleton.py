"""
=============================================================================
SKELETON MODUL: encoding_skeleton.py — Wordle Kripto (RSA Edition)
Projek Kelompok Matematika Diskrit 2
=============================================================================

PETUNJUK PENGGUNAAN BAGI ANGGOTA KELOMPOK:
File ini adalah TEMPLATE / SKELETON konversi teks dan sistem blok angka RSA.
Setiap fungsi dilengkapi docstring, rumus, dan petunjuk implementasi.

Aturan Pemetaan Alfabet Materi Dosen:
- A=00, B=01, C=02, ..., Z=25
- Setiap huruf direpresentasikan tepat oleh 2 digit angka.
- Kata 5 huruf menghasilkan string 10 digit angka.
  Contoh: BUNGA -> B=01, U=20, N=13, G=06, A=00 -> "0120130600"

Aturan Ukuran Blok 2N Digit:
- Blok terdiri dari 2N digit genap terbesar sehingga bilangan 2525...25 <= n.
- Contoh:
    n = 2537       -> 2525 <= 2537 < 252525       -> blok 4 digit (2 huruf)
    n = 2602632031 -> 2525252525 <= n < 252525252525 -> blok 10 digit (5 huruf)
=============================================================================
"""

ALFABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def huruf_ke_angka(huruf: str) -> str:
    """
    Mengonversi satu huruf kapital (A-Z) menjadi string 2 digit (00-25).
    Contoh: 'A' -> '00', 'B' -> '01', 'Z' -> '25'.

    Petunjuk:
    - Gunakan ord(huruf) - ord('A')
    - Format dengan f"{nilai:02d}"
    """
    # TODO: Implementasikan di sini
    pass


def angka_ke_huruf(dua_digit: str) -> str:
    """
    Mengonversi string 2 digit angka (00-25) menjadi satu karakter huruf kapital.
    Contoh: '00' -> 'A', '01' -> 'B', '25' -> 'Z'.

    Petunjuk:
    - Ubah dua_digit ke integer: val = int(dua_digit)
    - Validasi 0 <= val <= 25
    - Karakter: chr(ord('A') + val)
    """
    # TODO: Implementasikan di sini
    pass


def teks_ke_angka_str(teks: str) -> str:
    """
    Mengonversi seluruh string teks menjadi rangkaian digit angka 2-digit per huruf.
    Contoh: 'BUNGA' -> '0120130600'
    """
    # TODO: Implementasikan di sini
    pass


def angka_str_ke_teks(s: str) -> str:
    """
    Mengonversi string digit angka kembali menjadi teks huruf kapital.
    String diproses berpasangan 2 digit.
    Contoh: '0120130600' -> 'BUNGA'
    """
    # TODO: Implementasikan di sini
    pass


def hitung_ukuran_blok(n: int) -> int:
    """
    Menghitung ukuran blok 2N digit genap terbesar sedemikian rupa sehingga
    bilangan int('25' * N) <= n.

    Contoh:
    - n = 2537: '25' * 2 = 2525 <= 2537, '25' * 3 = 252525 > 2537 -> kembalikan 4
    - n = 2602632031: kembalikan 10

    Returns:
        int: Ukuran blok (bilangan genap)
    """
    # TODO: Implementasikan di sini
    pass


def bagi_blok(s: str, ukuran_blok: int, pad_char: str = "0") -> list:
    """
    Membagi string digit menjadi daftar integer blok berukuran `ukuran_blok` digit.
    Tambahkan padding pad_char di kanan pada blok terakhir jika kurang panjang.
    """
    # TODO: Implementasikan di sini
    pass


def gabung_blok(list_int: list, ukuran_blok: int) -> str:
    """
    Menggabungkan daftar integer blok menjadi satu string digit utuh
    dengan zero-padding kiri sepanjang `ukuran_blok` per elemen.
    """
    # TODO: Implementasikan di sini
    pass


def enkripsi_kata_game(kata: str, e: int, n: int) -> int:
    """
    Khusus mode Wordle Kripto:
    1. Validasi kata tepat 5 huruf kapital.
    2. Ubah kata ke string 10 digit: teks_ke_angka_str(kata).
    3. Konversi ke integer M = int(angka_str).
    4. Hitung C = M^e mod n (menggunakan enkripsi_blok dari rsa_core).
    5. Kembalikan C.
    """
    # TODO: Implementasikan di sini
    pass


def dekripsi_kata_game(C: int, d: int, n: int) -> str:
    """
    Khusus mode Wordle Kripto:
    1. Dekripsi C: M = C^d mod n (menggunakan dekripsi_blok dari rsa_core).
    2. Format M menjadi string 10 digit dengan zero-padding kiri: str(M).zfill(10).
    3. Decode ke kata 5 huruf: angka_str_ke_teks(s).
    4. Kembalikan kata.
    """
    # TODO: Implementasikan di sini
    pass

"""
Modul game_master.py — Wordle Kripto (RSA Edition)

Pengelola utama permainan dan pemegang rahasia kriptografi.
Sesuai PRD §4.3 (Batas Tanggung Jawab):
- Modul antarmuka (UI/CLI) hanya boleh menerima kunci publik (n, e),
  sandi misteri (C), dan hasil warna tebakan.
- Kunci privat (d) dan kata rahasia asli dienkapsulasi rapat di sini
  sampai permainan selesai dan fungsi buka_rahasia() dipanggil.
- Penerbitan sertifikat digital hasil permainan menggunakan pasangan
  kunci tanda tangan yang terpisah dari kunci permainan (F-12).
"""

import os
import random

from rsa_core import (
    buat_kunci,
    buat_kunci_acak,
    enkripsi_blok,
    dekripsi_blok,
    tanda_tangan,
    verifikasi_tanda_tangan,
)
from encoding import (
    enkripsi_kata_game,
    dekripsi_kata_game,
    teks_ke_angka_str,
)


class GameMaster:
    """
    GameMaster memegang kunci privat dan kata rahasia.
    """

    # Parameter default game (dari PRD §6)
    P_DEFAULT = 51001
    Q_DEFAULT = 51031
    E_DEFAULT = 65537
    N_DEFAULT = 2602632031
    D_DEFAULT = 154713473

    # Kunci tanda tangan terpisah (menggunakan data slide dosen: n=2537, e=13, d=937)
    # Ini memastikan tanda tangan tidak dapat digunakan untuk mendekripsi kata rahasia game
    SIGN_P = 43
    SIGN_Q = 59
    SIGN_N = 2537
    SIGN_E = 13
    SIGN_D = 937

    def __init__(
        self,
        p: int = None,
        q: int = None,
        e: int = None,
        ukuran_kunci: str = "default",
        daftar_kata_path: str = "kata.txt",
        seed: int = None,
    ):
        """
        Inisialisasi GameMaster.

        Parameters
        ----------
        p, q, e : int, optional
            Kunci manual jika ditentukan.
        ukuran_kunci : str, optional
            'default', 'kecil', 'sedang', atau 'besar'.
        daftar_kata_path : str, optional
            Path menuju file kata.txt.
        seed : int, optional
            Seed pengacakan untuk eksperimen reproduktif.
        """
        if seed is not None:
            random.seed(seed)

        # 1. Muat daftar kata
        self._daftar_kata = self.muat_kata(daftar_kata_path)

        # 2. Siapkan kunci RSA permainan
        if p is not None and q is not None and e is not None:
            self._n, self._e, self._d = buat_kunci(p, q, e, mode_game=True)
        elif ukuran_kunci.lower() == "default":
            self._n = self.N_DEFAULT
            self._e = self.E_DEFAULT
            self._d = self.D_DEFAULT
        else:
            self._n, self._e, self._d = buat_kunci_acak(ukuran_kunci, seed=seed)

        # 3. Siapkan pasangan kunci tanda tangan digital terpisah
        self._n_sign = self.SIGN_N
        self._e_sign = self.SIGN_E
        self._d_sign = self.SIGN_D

        # 4. Pilih kata rahasia acak dan enkripsi menjadi C
        self._kata_rahasia = random.choice(self._daftar_kata)
        self._M = int(teks_ke_angka_str(self._kata_rahasia))
        self._C = enkripsi_kata_game(self._kata_rahasia, self._e, self._n)
        self._nomor_puzzle = random.randint(100, 999)

    @property
    def kunci_publik(self) -> tuple:
        """Kunci publik (n, e) — aman ditampilkan ke pemain."""
        return self._n, self._e

    @property
    def sandi_misteri(self) -> int:
        """Ciphertext C dari kata rahasia — aman ditampilkan ke pemain."""
        return self._C

    @property
    def kata_terpilih(self) -> str:
        """Kata rahasia — hanya untuk pengujian atau GameMaster internal."""
        return self._kata_rahasia

    def nilai_tebakan(self, tebak: str) -> dict:
        """
        Mengenkrpsi kata tebakan pemain dengan kunci publik (n, e)
        dan membandingkannya dengan sandi misteri C.

        Parameters
        ----------
        tebak : str
            Kata tebakan 5 huruf.

        Returns
        -------
        dict
            {
                'benar': bool,          # True jika cipher_tebakan == sandi_misteri
                'cipher_tebakan': int   # Ciphertext tebakan
            }
        """
        tebak = tebak.strip().upper()
        c_tebak = enkripsi_kata_game(tebak, self._e, self._n)
        return {
            "benar": (c_tebak == self._C),
            "cipher_tebakan": c_tebak,
        }

    def warna_tebakan(self, tebak: str) -> list:
        """
        GameMaster mendekripsi sandi misteri dengan kunci privat d untuk
        memperoleh kata rahasia asli, lalu membandingkannya dengan kata tebakan
        untuk menentukan warna Wordle (dua tahap).

        Parameters
        ----------
        tebak : str
            Kata tebakan 5 huruf.

        Returns
        -------
        list[str]
            Daftar 5 string warna ('hijau', 'kuning', 'abu').
        """
        from wordle_engine import hitung_warna

        # Memastikan bahwa sandi misteri jika didekripsi memang menghasilkan kata rahasia
        kata_dekripsi = dekripsi_kata_game(self._C, self._d, self._n)
        return hitung_warna(kata_dekripsi, tebak.strip().upper())

    def buka_rahasia(self) -> dict:
        """
        Membuka kata rahasia beserta pembuktian matematis dekripsi RSA.
        Hanya dipanggil setelah permainan berakhir.

        Returns
        -------
        dict
            {
                'kata': str,
                'M': int,
                'C': int,
                'pembuktian': str
            }
        """
        m_dekripsi = dekripsi_blok(self._C, self._d, self._n)
        m_str = str(m_dekripsi).zfill(10)
        pembuktian = (
            f"C^d mod n = {self._C}^{self._d} mod {self._n} = "
            f"{m_str} -> {self._kata_rahasia}"
        )
        return {
            "kata": self._kata_rahasia,
            "M": self._M,
            "C": self._C,
            "pembuktian": pembuktian,
        }

    def terbitkan_sertifikat(self, hasil: dict) -> dict:
        """
        Menerbitkan sertifikat hasil permainan bertanda tangan digital RSA (F-12).

        Ringkasan hasil dikodekan sebagai bilangan integer R < n_sign:
            R = (menang_bit * 1000 + jumlah_tebakan * 100 + nomor_puzzle % 100)
            S = R^d_sign mod n_sign

        Parameters
        ----------
        hasil : dict
            {'menang': bool, 'jumlah_tebakan': int, 'nomor_puzzle': int}

        Returns
        -------
        dict
            {
                'R': int,
                'S': int,
                'n_sign': int,
                'e_sign': int
            }
        """
        menang_bit = 1 if hasil.get("menang", False) else 0
        tebakan = int(hasil.get("jumlah_tebakan", 6)) % 10
        puzzle = int(hasil.get("nomor_puzzle", self._nomor_puzzle)) % 100

        # R dipastikan positif dan lebih kecil dari n_sign (2537)
        R = (menang_bit * 1000 + tebakan * 100 + puzzle) % self._n_sign
        if R == 0:
            R = 1

        S = tanda_tangan(R, self._d_sign, self._n_sign)

        return {
            "R": R,
            "S": S,
            "n_sign": self._n_sign,
            "e_sign": self._e_sign,
        }

    def verifikasi_sertifikat(self, R: int, S: int, n_sign: int, e_sign: int) -> bool:
        """
        Memverifikasi keabsahan sertifikat hasil menggunakan kunci publik tanda tangan:
            S^e_sign mod n_sign == R

        Parameters
        ----------
        R : int
            Nilai ringkasan data.
        S : int
            Tanda tangan digital.
        n_sign : int
            Modulus tanda tangan.
        e_sign : int
            Eksponen publik tanda tangan.

        Returns
        -------
        bool
            True jika valid, False jika palsu/dimodifikasi.
        """
        return verifikasi_tanda_tangan(S, e_sign, n_sign, R)

    @staticmethod
    def muat_kata(path: str) -> list:
        """
        Membaca file kata dan memfilter kata 5 huruf A-Z.
        """
        abs_path = os.path.abspath(path)
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        kata_list = []
        for line in lines:
            w = line.strip().upper()
            if len(w) == 5 and w.isalpha() and w.isascii():
                kata_list.append(w)

        if not kata_list:
            raise ValueError(f"Tidak ada kata valid di '{abs_path}'.")

        return kata_list

"""
Unit test untuk modul rsa_core.py — Wordle Kripto (RSA Edition)
"""

import math
import random
import unittest

from rsa_core import (
    fpb,
    euclid_diperluas,
    cari_d,
    eksponen_modular,
    cek_prima_percobaan,
    miller_rabin,
    cek_prima,
    buat_prima_acak,
    buat_kunci,
    buat_kunci_acak,
    enkripsi_blok,
    dekripsi_blok,
    tanda_tangan,
    verifikasi_tanda_tangan,
)


class TestFPB(unittest.TestCase):
    def test_kasus_dasar(self):
        self.assertEqual(fpb(48, 18), 6)
        self.assertEqual(fpb(13, 2436), 1)
        self.assertEqual(fpb(0, 5), 5)
        self.assertEqual(fpb(100, 0), 100)

    def test_kesesuaian_dengan_math_gcd(self):
        """Membandingkan fpb buatan sendiri dengan math.gcd pada 1000 pasangan acak."""
        random.seed(42)
        for _ in range(1000):
            a = random.randint(1, 10_000_000)
            b = random.randint(1, 10_000_000)
            self.assertEqual(fpb(a, b), math.gcd(a, b))


class TestEuclidDiperluas(unittest.TestCase):
    def test_identitas_bezout(self):
        gcd, x, y = euclid_diperluas(13, 2436)
        self.assertEqual(gcd, 1)
        self.assertEqual(13 * x + 2436 * y, 1)

    def test_pasangan_acak(self):
        random.seed(123)
        for _ in range(100):
            a = random.randint(2, 50000)
            b = random.randint(2, 50000)
            gcd, x, y = euclid_diperluas(a, b)
            self.assertEqual(a * x + b * y, gcd)
            self.assertEqual(gcd, math.gcd(a, b))


class TestCariD(unittest.TestCase):
    def test_data_dosen(self):
        # Dari slide dosen: e=13, φ=(43-1)*(59-1)=2436 -> d=937
        d = cari_d(13, 2436)
        self.assertEqual(d, 937)
        self.assertEqual((13 * d) % 2436, 1)

    def test_parameter_default_game(self):
        # p=51001, q=51031 -> φ=2602530000, e=65537 -> d=154713473
        d = cari_d(65537, 2602530000)
        self.assertEqual(d, 154713473)
        self.assertEqual((65537 * d) % 2602530000, 1)

    def test_error_tidak_koprima(self):
        # FPB(6, 9) = 3 != 1
        with self.assertRaises(ValueError):
            cari_d(6, 9)


class TestEksponenModular(unittest.TestCase):
    def test_data_slide_dosen_enkripsi_stop(self):
        # Dari slide: n=2537, e=13, STOP -> blok 1819 dan 1415
        self.assertEqual(eksponen_modular(1819, 13, 2537), 2081)
        self.assertEqual(eksponen_modular(1415, 13, 2537), 2182)

    def test_data_slide_dosen_dekripsi_stop(self):
        # n=2537, d=937
        self.assertEqual(eksponen_modular(2081, 937, 2537), 1819)
        self.assertEqual(eksponen_modular(2182, 937, 2537), 1415)

    def test_data_slide_dosen_dekripsi_help(self):
        # Cipher 0981 dan 0461 -> 0704 (HE) dan 1115 (LP) -> HELP
        self.assertEqual(eksponen_modular(981, 937, 2537), 704)
        self.assertEqual(eksponen_modular(461, 937, 2537), 1115)

    def test_kesesuaian_dengan_pow_bawaan(self):
        """Membandingkan kuadrat-dan-kali dengan pow(a,b,m) pada 1000 kasus acak."""
        random.seed(999)
        for _ in range(1000):
            base = random.randint(0, 100000)
            exp = random.randint(0, 10000)
            mod = random.randint(2, 100000)
            self.assertEqual(eksponen_modular(base, exp, mod), pow(base, exp, mod))


class TestCekPrima(unittest.TestCase):
    def test_nilai_spesifik(self):
        self.assertFalse(cek_prima(2537))  # 43 * 59 komposit
        self.assertTrue(cek_prima(43))
        self.assertTrue(cek_prima(59))
        self.assertTrue(cek_prima(65537))
        self.assertTrue(cek_prima(51001))
        self.assertTrue(cek_prima(51031))
        self.assertFalse(cek_prima(1))
        self.assertFalse(cek_prima(0))

    def test_konsistensi_miller_rabin_vs_percobaan(self):
        """Uji konsistensi Miller-Rabin dengan pembagian percobaan untuk bilangan ganjil < 5000."""
        for n in range(3, 5000, 2):
            self.assertEqual(miller_rabin(n, k=15), cek_prima_percobaan(n), f"Inkonsistensi pada n={n}")


class TestBuatKunci(unittest.TestCase):
    def test_kunci_slide_dosen(self):
        # p=43, q=59, e=13 -> (2537, 13, 937) dengan mode_game=False
        n, e, d = buat_kunci(43, 59, 13, mode_game=False)
        self.assertEqual(n, 2537)
        self.assertEqual(e, 13)
        self.assertEqual(d, 937)

    def test_kunci_default_game(self):
        n, e, d = buat_kunci(51001, 51031, 65537, mode_game=True)
        self.assertEqual(n, 2602632031)
        self.assertEqual(e, 65537)
        self.assertEqual(d, 154713473)

    def test_validasi_p_sama_dengan_q(self):
        with self.assertRaises(ValueError):
            buat_kunci(43, 43, 13, mode_game=False)

    def test_validasi_p_bukan_prima(self):
        with self.assertRaises(ValueError):
            buat_kunci(42, 59, 13, mode_game=False)

    def test_validasi_e_di_luar_rentang(self):
        with self.assertRaises(ValueError):
            buat_kunci(43, 59, 0, mode_game=False)
        with self.assertRaises(ValueError):
            buat_kunci(43, 59, 1, mode_game=False)
        with self.assertRaises(ValueError):
            buat_kunci(43, 59, 2436, mode_game=False)

    def test_validasi_gcd_tidak_satu(self):
        # φ=2436 habis dibagi 2, jadi e=14 memiliki gcd=2
        with self.assertRaises(ValueError):
            buat_kunci(43, 59, 14, mode_game=False)

    def test_validasi_n_terlalu_kecil_pada_mode_game(self):
        # n = 2537 < 2525252525 harus ditolak jika mode_game=True
        with self.assertRaises(ValueError):
            buat_kunci(43, 59, 13, mode_game=True)


class TestTandaTanganDigital(unittest.TestCase):
    def test_data_slide_meet_at_noon(self):
        # Slide dosen: n=2537, e=13, d=937
        # Blok pesan: 1204, 0419, 0019 (19), 1314, 1413
        # Ditandatangani S = R^d mod n -> 817, 555, 1310, 2173, 1026
        n = 2537
        e = 13
        d = 937

        pesan_blok = [1204, 419, 19, 1314, 1413]
        sig_diharapkan = [817, 555, 1310, 2173, 1026]

        for R, S_expected in zip(pesan_blok, sig_diharapkan):
            S = tanda_tangan(R, d, n)
            self.assertEqual(S, S_expected)
            # Verifikasi tanda tangan asli
            self.assertTrue(verifikasi_tanda_tangan(S, e, n, R))
            # Verifikasi jika tanda tangan diubah 1 angka harus gagal
            self.assertFalse(verifikasi_tanda_tangan(S + 1, e, n, R))


if __name__ == "__main__":
    unittest.main()

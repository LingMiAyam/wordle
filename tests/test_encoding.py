"""
Unit test untuk modul encoding.py — Wordle Kripto (RSA Edition)
"""

import unittest

from encoding import (
    huruf_ke_angka,
    angka_ke_huruf,
    teks_ke_angka_str,
    angka_str_ke_teks,
    hitung_ukuran_blok,
    bagi_blok,
    gabung_blok,
    enkripsi_teks,
    dekripsi_teks,
    enkripsi_kata_game,
    dekripsi_kata_game,
)


class TestKonversiDasar(unittest.TestCase):
    def test_huruf_ke_angka(self):
        self.assertEqual(huruf_ke_angka("A"), "00")
        self.assertEqual(huruf_ke_angka("B"), "01")
        self.assertEqual(huruf_ke_angka("Z"), "25")
        with self.assertRaises(ValueError):
            huruf_ke_angka("a")  # hanya huruf kapital
        with self.assertRaises(ValueError):
            huruf_ke_angka("1")

    def test_angka_ke_huruf(self):
        self.assertEqual(angka_ke_huruf("00"), "A")
        self.assertEqual(angka_ke_huruf("01"), "B")
        self.assertEqual(angka_ke_huruf("25"), "Z")
        with self.assertRaises(ValueError):
            angka_ke_huruf("26")
        with self.assertRaises(ValueError):
            angka_ke_huruf("99")


class TestTeksAngka(unittest.TestCase):
    def test_teks_ke_angka_str(self):
        self.assertEqual(teks_ke_angka_str("BUNGA"), "0120130600")
        self.assertEqual(teks_ke_angka_str("STOP"), "18191415")
        self.assertEqual(teks_ke_angka_str("ZZZZZ"), "2525252525")

    def test_angka_str_ke_teks(self):
        self.assertEqual(angka_str_ke_teks("0120130600"), "BUNGA")
        self.assertEqual(angka_str_ke_teks("18191415"), "STOP")
        self.assertEqual(angka_str_ke_teks("2525252525"), "ZZZZZ")

    def test_error_panjang_ganjil(self):
        with self.assertRaises(ValueError):
            angka_str_ke_teks("012")


class TestUkuranBlok(unittest.TestCase):
    def test_aturan_materi_dosen(self):
        # n = 2537: 2525 <= 2537 < 252525 -> blok 4 digit (2 huruf)
        self.assertEqual(hitung_ukuran_blok(2537), 4)

        # n = 2602632031: 2525252525 <= n < 252525252525 -> blok 10 digit (5 huruf)
        self.assertEqual(hitung_ukuran_blok(2602632031), 10)


class TestBagiDanGabungBlok(unittest.TestCase):
    def test_bagi_blok_stop(self):
        # '18191415' dengan ukuran 4 digit -> [1819, 1415]
        self.assertEqual(bagi_blok("18191415", 4), [1819, 1415])

    def test_bagi_blok_bunga(self):
        # '0120130600' dengan ukuran 10 digit -> [120130600]
        self.assertEqual(bagi_blok("0120130600", 10), [120130600])

    def test_gabung_blok(self):
        self.assertEqual(gabung_blok([1819, 1415], 4), "18191415")
        self.assertEqual(gabung_blok([120130600], 10), "0120130600")


class TestEnkripsiDekripsiTeksSlideDosen(unittest.TestCase):
    def test_slide_stop_dan_help(self):
        # Data slide dosen: n=2537, e=13, d=937
        # Enkripsi STOP -> [2081, 2182]
        cipher = enkripsi_teks("STOP", 13, 2537)
        self.assertEqual(cipher, [2081, 2182])

        # Dekripsi [0981, 0461] -> HELP
        hasil_teks = dekripsi_teks([981, 461], 937, 2537, panjang_asli=4)
        self.assertEqual(hasil_teks, "HELP")


class TestModeGameWordle(unittest.TestCase):
    def test_data_default_bunga_dan_bukan(self):
        n = 2602632031
        e = 65537
        d = 154713473

        # BUNGA -> C = 587403072
        c_bunga = enkripsi_kata_game("BUNGA", e, n)
        self.assertEqual(c_bunga, 587403072)
        dekrip_bunga = dekripsi_kata_game(c_bunga, d, n)
        self.assertEqual(dekrip_bunga, "BUNGA")

        # BUKAN -> C = 293955741
        c_bukan = enkripsi_kata_game("BUKAN", e, n)
        self.assertEqual(c_bukan, 293955741)
        dekrip_bukan = dekripsi_kata_game(c_bukan, d, n)
        self.assertEqual(dekrip_bukan, "BUKAN")

    def test_kasus_ekstrem_zzzzz(self):
        # M = 2525252525 (nilai maksimum untuk 5 huruf)
        n = 2602632031
        e = 65537
        d = 154713473

        c_zzzzz = enkripsi_kata_game("ZZZZZ", e, n)
        dekrip_zzzzz = dekripsi_kata_game(c_zzzzz, d, n)
        self.assertEqual(dekrip_zzzzz, "ZZZZZ")

    def test_kasus_huruf_awal_a(self):
        # Memastikan zero-padding kiri bekerja (misal 'APPLE' dimulai dari '00')
        n = 2602632031
        e = 65537
        d = 154713473

        c_apple = enkripsi_kata_game("APPLE", e, n)
        dekrip_apple = dekripsi_kata_game(c_apple, d, n)
        self.assertEqual(dekrip_apple, "APPLE")


if __name__ == "__main__":
    unittest.main()

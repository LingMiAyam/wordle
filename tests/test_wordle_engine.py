"""
Unit test untuk modul wordle_engine.py — Wordle Kripto (RSA Edition)
"""

import unittest

from wordle_engine import (
    hitung_warna,
    WordleEngine,
    MAKS_TEBAKAN,
    WARNA_HIJAU,
    WARNA_KUNING,
    WARNA_ABU,
)


class MockGameMaster:
    """Mock GameMaster sederhana untuk menguji WordleEngine secara terisolasi."""

    def __init__(self, kata_rahasia: str = "CRANE"):
        self._rahasia = kata_rahasia
        self._n = 2602632031
        self._e = 65537

    @property
    def kunci_publik(self):
        return self._n, self._e

    @property
    def sandi_misteri(self):
        return 999999

    def nilai_tebakan(self, tebak: str):
        tebak = tebak.strip().upper()
        return {
            "benar": (tebak == self._rahasia),
            "cipher_tebakan": 123456 if tebak != self._rahasia else 999999,
        }

    def warna_tebakan(self, tebak: str):
        return hitung_warna(self._rahasia, tebak)


class TestHitungWarna(unittest.TestCase):
    def test_kasus_prd_huruf_kembar_abcde_aaxxx(self):
        # PRD §4.1: rahasia ABCDE, tebakan AAXXX -> hanya A pertama yang hijau, A kedua abu-abu
        warna = hitung_warna("ABCDE", "AAXXX")
        self.assertEqual(
            warna,
            [WARNA_HIJAU, WARNA_ABU, WARNA_ABU, WARNA_ABU, WARNA_ABU],
        )

    def test_kasus_speed_vs_eeeds(self):
        # rahasia SPEED: S(0), P(1), E(2), E(3), D(4)
        # tebakan EEEDS: E(0), E(1), E(2), D(3), S(4)
        # Posisi 2: E==E (hijau)
        # Posisi 0: E cocok dengan E rahasia posisi 3 (kuning)
        # Posisi 1: E tidak ada lagi kemunculan E di rahasia (abu)
        # Posisi 3: D cocok dengan D rahasia (kuning)
        # Posisi 4: S cocok dengan S rahasia (kuning)
        warna = hitung_warna("SPEED", "EEEDS")
        self.assertEqual(
            warna,
            [WARNA_KUNING, WARNA_ABU, WARNA_HIJAU, WARNA_KUNING, WARNA_KUNING],
        )

    def test_kasus_abbbc_vs_bbbaa(self):
        # rahasia ABBBC (A, B, B, B, C)
        # tebakan BBBAA (B, B, B, A, A)
        # Hijau: posisi 1 (B=B), posisi 2 (B=B)
        # Kuning: posisi 0 (B cocok dengan B rahasia posisi 3), posisi 3 (A cocok dengan A rahasia posisi 0)
        # Abu: posisi 4 (A kedua di tebakan, tapi kemunculan A di rahasia sudah habis)
        warna = hitung_warna("ABBBC", "BBBAA")
        self.assertEqual(
            warna,
            [WARNA_KUNING, WARNA_HIJAU, WARNA_HIJAU, WARNA_KUNING, WARNA_ABU],
        )

    def test_tebakan_benar_semua_hijau(self):
        warna = hitung_warna("CRANE", "CRANE")
        self.assertEqual(warna, [WARNA_HIJAU] * 5)

    def test_tidak_ada_huruf_yang_cocok(self):
        warna = hitung_warna("ABCDE", "FGHIJ")
        self.assertEqual(warna, [WARNA_ABU] * 5)


class TestWordleEngineValidasiDanSiklus(unittest.TestCase):
    def setUp(self):
        self.daftar_kata = ["CRANE", "SLATE", "AUDIO", "WORDS", "PLANT", "LIGHT", "CANDY"]
        self.gm = MockGameMaster(kata_rahasia="CRANE")
        self.engine = WordleEngine(self.gm, self.daftar_kata)

    def test_validasi_panjang_huruf(self):
        with self.assertRaises(ValueError):
            self.engine.tebak("CRAN")
        with self.assertRaises(ValueError):
            self.engine.tebak("CRANES")

    def test_validasi_karakter_non_alfabet(self):
        with self.assertRaises(ValueError):
            self.engine.tebak("CRAN1")
        with self.assertRaises(ValueError):
            self.engine.tebak("CR-NE")

    def test_validasi_kata_tidak_ada_di_kamus(self):
        with self.assertRaises(ValueError):
            self.engine.tebak("ZZZZZ")

    def test_alur_menang_di_tebakan_kedua(self):
        # Tebakan 1: salah
        res1 = self.engine.tebak("SLATE")
        self.assertFalse(res1["menang"])
        self.assertFalse(res1["kalah"])
        self.assertEqual(res1["sisa_tebakan"], 5)

        # Tebakan 2: benar
        res2 = self.engine.tebak("CRANE")
        self.assertTrue(res2["menang"])
        self.assertFalse(res2["kalah"])
        self.assertEqual(res2["sisa_tebakan"], 4)

        status = self.engine.status()
        self.assertFalse(status["aktif"])
        self.assertTrue(status["menang"])

        # Mencoba menebak lagi setelah menang harus memicu RuntimeError
        with self.assertRaises(RuntimeError):
            self.engine.tebak("AUDIO")

    def test_alur_kalah_setelah_enam_kali(self):
        for _ in range(5):
            self.engine.tebak("SLATE")
            self.assertFalse(self.engine.status()["kalah"])

        res6 = self.engine.tebak("SLATE")
        self.assertTrue(res6["kalah"])
        self.assertFalse(res6["menang"])
        self.assertEqual(res6["sisa_tebakan"], 0)

        status = self.engine.status()
        self.assertFalse(status["aktif"])
        self.assertTrue(status["kalah"])

        # Menebak setelah kalah harus memicu RuntimeError
        with self.assertRaises(RuntimeError):
            self.engine.tebak("CRANE")


if __name__ == "__main__":
    unittest.main()

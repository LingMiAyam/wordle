"""
Modul wordle_engine.py — Wordle Kripto (RSA Edition)

Mengatur aturan permainan Wordle:
- Maksimal 6 kesempatan tebakan untuk kata 5 huruf.
- Penilaian warna berbasis dua tahap (hijau dahulu, lalu kuning)
  dengan penanganan duplikasi huruf kembar yang akurat sesuai aturan Wordle resmi.
- Validasi ketat terhadap input tebakan (panjang, karakter, daftar kamus).
- Riwayat sesi dan pelacakan status menang/kalah.
"""

MAKS_TEBAKAN = 6
WARNA_HIJAU = "hijau"
WARNA_KUNING = "kuning"
WARNA_ABU = "abu"


def hitung_warna(rahasia: str, tebakan: str) -> list:
    """
    Menghitung warna penilaian untuk setiap huruf tebakan berdasarkan kata rahasia.

    Aturan Dua Tahap Wordle:
    1. Tahap 1 (Hijau):
       Memeriksa kecocokan posisi tepat (tebakan[i] == rahasia[i]).
       Tandai posisi tersebut pada kata rahasia dan tebakan sebagai sudah terpakai.

    2. Tahap 2 (Kuning & Abu-abu):
       Untuk setiap huruf tebakan yang belum hijau:
       Cari kemunculan huruf tersebut pada rahasia di posisi yang belum terpakai.
       Jika ada, beri warna kuning dan tandai posisi rahasia tersebut.
       Jika tidak ada lagi kemunculan yang tersedia, beri warna abu-abu.

    Contoh:
    - rahasia='ABCDE', tebakan='AAXXX' -> ['hijau', 'abu', 'abu', 'abu', 'abu']
    - rahasia='SPEED', tebakan='EEEDS' -> ['kuning', 'abu', 'hijau', 'kuning', 'kuning']
    - rahasia='CRANE', tebakan='CRANE' -> ['hijau', 'hijau', 'hijau', 'hijau', 'hijau']

    Parameters
    ----------
    rahasia : str
        Kata rahasia 5 huruf kapital.
    tebakan : str
        Kata tebakan 5 huruf kapital.

    Returns
    -------
    list[str]
        Daftar 5 string warna: 'hijau', 'kuning', atau 'abu'.
    """
    rahasia = rahasia.upper()
    tebakan = tebakan.upper()

    warna = [WARNA_ABU] * 5
    dipakai_rahasia = [False] * 5
    dipakai_tebakan = [False] * 5

    # Tahap 1: Evaluasi Hijau (Posisi Tepat)
    for i in range(5):
        if tebakan[i] == rahasia[i]:
            warna[i] = WARNA_HIJAU
            dipakai_rahasia[i] = True
            dipakai_tebakan[i] = True

    # Tahap 2: Evaluasi Kuning (Huruf Ada di Posisi Lain)
    for i in range(5):
        if dipakai_tebakan[i]:
            continue
        for j in range(5):
            if not dipakai_rahasia[j] and tebakan[i] == rahasia[j]:
                warna[i] = WARNA_KUNING
                dipakai_rahasia[j] = True
                break

    return warna


class WordleEngine:
    """
    Mesin pengatur alur permainan Wordle Kripto.

    Berinteraksi dengan GameMaster untuk memverifikasi kesesuaian sandi misteri
    dan memperoleh umpan balik warna tanpa mengekspos kata rahasia kepada pemain.
    """

    def __init__(self, game_master, daftar_kata: list):
        """
        Inisialisasi sesi permainan Wordle.

        Parameters
        ----------
        game_master : GameMaster
            Objek GameMaster pengelola kunci dan rahasia.
        daftar_kata : list[str]
            Daftar kata yang valid sebagai tebakan.
        """
        self._gm = game_master
        self._daftar_kata = set(k.strip().upper() for k in daftar_kata)
        self._riwayat = []
        self._menang = False
        self._kalah = False
        self._selesai = False

    def tebak(self, kata: str) -> dict:
        """
        Memproses satu tebakan dari pemain.

        Parameters
        ----------
        kata : str
            Tebakan kata dari pemain.

        Returns
        -------
        dict
            {
                'warna': list[str],          # Warna tiap huruf
                'cipher_tebakan': int,        # Nilai C dari tebakan
                'menang': bool,              # Apakah tebakan benar
                'sisa_tebakan': int,         # Sisa tebakan
                'kalah': bool,               # Apakah kesempatan habis dan belum menang
            }

        Raises
        ------
        RuntimeError
            Jika permainan sudah selesai (menang atau kalah).
        ValueError
            Jika kata tidak 5 huruf, bukan A-Z, atau tidak ada dalam daftar.
        """
        if self._selesai:
            raise RuntimeError("Permainan sudah berakhir. Mulai permainan baru.")

        kata_bersih = kata.strip().upper()

        if len(kata_bersih) != 5:
            raise ValueError(f"Tebakan harus tepat 5 huruf, diterima '{kata_bersih}' ({len(kata_bersih)} huruf).")

        if not (kata_bersih.isalpha() and kata_bersih.isascii()):
            raise ValueError("Tebakan hanya boleh berisi huruf A-Z tanpa angka atau simbol.")

        if kata_bersih not in self._daftar_kata:
            raise ValueError(f"Kata '{kata_bersih}' tidak ada dalam daftar kata valid.")

        # Nilai tebakan melalui enkripsi RSA di GameMaster
        hasil_nilai = self._gm.nilai_tebakan(kata_bersih)
        cipher_tebakan = hasil_nilai["cipher_tebakan"]
        benar = hasil_nilai["benar"]

        # Hitung warna dari GameMaster
        warna = self._gm.warna_tebakan(kata_bersih)

        self._riwayat.append(
            {
                "kata": kata_bersih,
                "warna": warna,
                "cipher_tebakan": cipher_tebakan,
                "benar": benar,
            }
        )

        if benar:
            self._menang = True
            self._selesai = True
        elif len(self._riwayat) >= MAKS_TEBAKAN:
            self._kalah = True
            self._selesai = True

        return {
            "warna": warna,
            "cipher_tebakan": cipher_tebakan,
            "menang": self._menang,
            "sisa_tebakan": MAKS_TEBAKAN - len(self._riwayat),
            "kalah": self._kalah,
        }

    def status(self) -> dict:
        """
        Mengembalikan status sesi permainan terkini.

        Returns
        -------
        dict
            {
                'aktif': bool,
                'menang': bool,
                'kalah': bool,
                'jumlah_tebakan': int,
                'sisa': int
            }
        """
        return {
            "aktif": not self._selesai,
            "menang": self._menang,
            "kalah": self._kalah,
            "jumlah_tebakan": len(self._riwayat),
            "sisa": MAKS_TEBAKAN - len(self._riwayat),
        }

    def riwayat(self) -> list:
        """
        Mengembalikan salinan riwayat seluruh tebakan yang telah dilakukan.

        Returns
        -------
        list[dict]
            Daftar catatan tebakan.
        """
        return list(self._riwayat)

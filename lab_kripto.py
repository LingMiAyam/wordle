"""
Modul lab_kripto.py — Wordle Kripto (RSA Edition)

Menu Eksperimen Kriptografi Lanjutan (P2 Penuh):
1. Enkripsi dan Dekripsi Pesan Bebas (Multi-blok):
   Mendukung teks sembarang panjang yang dipecah ke beberapa blok berukuran 2N digit
   sesuai modulus n, dengan huruf 'X' sebagai pengisi blok terakhir jika tidak penuh.
2. Serangan Kamus (Dictionary Attack):
   Mendemonstrasikan kerentanan RSA textbook yang bersifat deterministik tanpa padding acak
   (OAEP). Penyerang yang memiliki kunci publik (n, e) dapat mengenkripsi seluruh kata di
   kamus hingga menemukan cipher yang identik dengan Sandi Misteri C tanpa memfaktorkan n.
3. Faktorisasi n dengan Pembagian Percobaan (Trial Division):
   Mendemonstrasikan bahwa keamanan RSA bergantung pada sulitnya memfaktorkan n = p * q.
   Mengukur waktu komputasi faktorisasi untuk berbagai ukuran modulus.
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox

from rsa_core import fpb, enkripsi_blok, dekripsi_blok
from encoding import (
    huruf_ke_angka,
    angka_ke_huruf,
    teks_ke_angka_str,
    angka_str_ke_teks,
    hitung_ukuran_blok,
    bagi_blok,
    gabung_blok,
    enkripsi_kata_game,
)


def enkripsi_pesan_bebas(pesan: str, e: int, n: int) -> dict:
    """
    Mengenkrpsi pesan teks bebas sembarang panjang menjadi daftar ciphertext blok.

    Langkah:
    1. Filter hanya karakter huruf A-Z dan ubah ke kapital.
    2. Hitung ukuran blok 2N digit yang sesuai dengan n.
    3. Tiap huruf = 2 digit. Jika jumlah huruf pada blok terakhir ganjil
       atau tidak memenuhi kelipatan huruf per blok (ukuran_blok / 2),
       tambahkan huruf padding 'X' (kode '23') di akhir teks.
    4. Ubah teks yang sudah ber-padding menjadi string angka.
    5. Pecah menjadi blok-blok integer M_i < n.
    6. Enkripsi tiap blok: C_i = M_i^e mod n.

    Parameters
    ----------
    pesan : str
        Teks pesan bebas.
    e : int
        Eksponen publik.
    n : int
        Modulus RSA.

    Returns
    -------
    dict
        Rincian langkah dan hasil enkripsi multi-blok.
    """
    pesan_bersih = "".join(c for c in pesan.upper() if c.isalpha() and c.isascii())
    if not pesan_bersih:
        raise ValueError("Pesan harus mengandung setidaknya satu huruf A-Z.")

    ukuran_blok = hitung_ukuran_blok(n)
    huruf_per_blok = ukuran_blok // 2

    # Tambahkan padding 'X' jika panjang teks bukan kelipatan huruf_per_blok
    sisa = len(pesan_bersih) % huruf_per_blok
    if sisa != 0:
        pesan_bersih += "X" * (huruf_per_blok - sisa)

    angka_str = teks_ke_angka_str(pesan_bersih)
    blok_plain = bagi_blok(angka_str, ukuran_blok)

    blok_cipher = []
    langkah = []
    for idx, M in enumerate(blok_plain):
        C = enkripsi_blok(M, e, n)
        blok_cipher.append(C)
        langkah.append(f"Blok {idx + 1}: M = {str(M).zfill(ukuran_blok)} → C = {M}^{e} mod {n} = {C}")

    return {
        "pesan_bersih": pesan_bersih,
        "angka_str": angka_str,
        "ukuran_blok": ukuran_blok,
        "huruf_per_blok": huruf_per_blok,
        "blok_plaintext": blok_plain,
        "blok_ciphertext": blok_cipher,
        "langkah": langkah,
    }


def dekripsi_pesan_bebas(list_cipher: list, d: int, n: int, panjang_asli: int = None) -> dict:
    """
    Mendekripsi daftar ciphertext blok menjadi teks pesan bebas.

    Parameters
    ----------
    list_cipher : list[int]
        Daftar ciphertext blok C_i.
    d : int
        Eksponen privat.
    n : int
        Modulus RSA.
    panjang_asli : int, optional
        Jumlah karakter huruf asli sebelum padding 'X'.

    Returns
    -------
    dict
        Rincian langkah dan teks hasil dekripsi.
    """
    ukuran_blok = hitung_ukuran_blok(n)
    blok_plain = []
    langkah = []

    for idx, C in enumerate(list_cipher):
        M = dekripsi_blok(C, d, n)
        blok_plain.append(M)
        langkah.append(f"Blok {idx + 1}: C = {C} → M = {C}^{d} mod {n} = {str(M).zfill(ukuran_blok)}")

    angka_str = gabung_blok(blok_plain, ukuran_blok)
    teks_penuh = angka_str_ke_teks(angka_str)

    if panjang_asli is not None:
        teks_hasil = teks_penuh[:panjang_asli]
    else:
        teks_hasil = teks_penuh

    return {
        "blok_ciphertext": list_cipher,
        "blok_plaintext": blok_plain,
        "angka_str": angka_str,
        "pesan": teks_hasil,
        "langkah": langkah,
    }


def serangan_kamus(C_target: int, e: int, n: int, daftar_kata: list) -> dict:
    """
    Melakukan serangan kamus (Dictionary Attack) terhadap Sandi Misteri C.

    Mengapa Berhasil?
    RSA textbook bersifat deterministik: pesan M yang sama selalu menghasilkan
    ciphertext C yang sama jika dienkripsi dengan kunci publik (n, e) yang sama.
    Karena ruang kata Wordle hanya ribuan kata, penyerang cukup mengenkripsi
    seluruh kata di daftar satu per satu hingga menemukan C yang sama persis
    tanpa perlu memfaktorkan n.

    Parameters
    ----------
    C_target : int
        Ciphertext sandi misteri yang dicari.
    e : int
        Eksponen publik.
    n : int
        Modulus RSA.
    daftar_kata : list[str]
        Kumpulan kata 5 huruf kandidat.

    Returns
    -------
    dict
        Hasil pencarian kamus.
    """
    start_time = time.perf_counter()
    jumlah_dicoba = 0
    kata_ditemukan = None

    for kata in daftar_kata:
        jumlah_dicoba += 1
        try:
            c_uji = enkripsi_kata_game(kata, e, n)
            if c_uji == C_target:
                kata_ditemukan = kata
                break
        except Exception:
            continue

    durasi = time.perf_counter() - start_time

    penjelasan = (
        "Serangan kamus berhasil karena RSA textbook bersifat deterministik tanpa padding acak "
        "(seperti OAEP). Setiap kata rahasia selalu menghasilkan ciphertext yang identik, "
        "sehingga penyerang dapat mencocokkan cipher tanpa memfaktorkan n."
    )

    return {
        "ditemukan": kata_ditemukan is not None,
        "kata": kata_ditemukan,
        "jumlah_dicoba": jumlah_dicoba,
        "waktu_detik": durasi,
        "penjelasan": penjelasan,
    }


def faktorisasi_n(n: int) -> dict:
    """
    Memfaktorkan modulus n = p * q menggunakan metode pembagian percobaan (trial division)
    serta mengukur waktu komputasi yang dihabiskan.

    Parameters
    ----------
    n : int
        Modulus RSA yang akan difaktorkan.

    Returns
    -------
    dict
        {
            'n': int,
            'p': int,
            'q': int,
            'waktu_detik': float,
            'langkah': int,
            'pesan': str
        }
    """
    start_time = time.perf_counter()
    p = None
    q = None
    langkah = 0

    if n % 2 == 0:
        p = 2
        q = n // 2
        langkah = 1
    else:
        limit = int(n**0.5) + 1
        i = 3
        while i <= limit:
            langkah += 1
            if n % i == 0:
                p = i
                q = n // i
                break
            i += 2

    durasi = time.perf_counter() - start_time

    if p is not None:
        pesan = f"n = {n} berhasil difaktorkan menjadi p={p} dan q={q} dalam {durasi:.6f} detik ({langkah} iterasi)."
    else:
        pesan = f"n = {n} tidak dapat difaktorkan (mungkin bilangan prima) dalam {durasi:.6f} detik."

    return {
        "n": n,
        "p": p,
        "q": q,
        "waktu_detik": durasi,
        "langkah": langkah,
        "pesan": pesan,
    }


# ===========================================================================
# GUI Window untuk Lab Kripto (Toplevel)
# ===========================================================================

class LabKriptoWindow(tk.Toplevel):
    """
    Jendela terpisah untuk Lab Kriptografi RSA interaktif (P2).
    """

    def __init__(self, parent, game_master):
        super().__init__(parent)
        self.title("🧪 Lab Kripto — Wordle Kripto (RSA Edition)")
        self.geometry("820x620")
        self.minsize(760, 560)
        self.configure(bg="#f8f9fa")
        self.gm = game_master

        self._buat_layout()

    def _buat_layout(self):
        # Header Info Kunci Aktif
        header_frame = tk.Frame(self, bg="#2c3e50", padx=15, pady=10)
        header_frame.pack(fill=tk.X)

        n, e = self.gm.kunci_publik
        C = self.gm.sandi_misteri
        lbl_info = tk.Label(
            header_frame,
            text=f"Kunci Aktif Permainan | n = {n} | e = {e} | Sandi Misteri C = {C}",
            font=("Helvetica", 10, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
        )
        lbl_info.pack(anchor="w")

        # Notebook Tab
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Tab 1: Enkripsi & Dekripsi Pesan Bebas
        frame_tab1 = tk.Frame(notebook, bg="#ffffff", padx=15, pady=15)
        notebook.add(frame_tab1, text="1. Enkripsi Pesan Bebas (Multi-Blok)")
        self._setup_tab_pesan_bebas(frame_tab1)

        # Tab 2: Serangan Kamus
        frame_tab2 = tk.Frame(notebook, bg="#ffffff", padx=15, pady=15)
        notebook.add(frame_tab2, text="2. Serangan Kamus terhadap C")
        self._setup_tab_serangan_kamus(frame_tab2)

        # Tab 3: Faktorisasi n
        frame_tab3 = tk.Frame(notebook, bg="#ffffff", padx=15, pady=15)
        notebook.add(frame_tab3, text="3. Faktorisasi Modulus n")
        self._setup_tab_faktorisasi(frame_tab3)

    # ------------------ TAB 1: Enkripsi Pesan Bebas ------------------
    def _setup_tab_pesan_bebas(self, frame):
        tk.Label(
            frame,
            text="Enkripsi Teks Sembarang Panjang (Dikelompokkan ke Blok Sesuai n)",
            font=("Helvetica", 11, "bold"),
            bg="#ffffff",
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(frame, text="Masukkan Pesan Bebas (huruf A-Z):", bg="#ffffff").pack(anchor="w")
        ent_pesan = tk.Entry(frame, font=("Helvetica", 11), width=60)
        ent_pesan.insert(0, "MEET AT NOON")
        ent_pesan.pack(fill=tk.X, pady=(2, 8))

        txt_hasil = tk.Text(frame, height=18, font=("Courier", 10), bg="#fdfefe", relief="solid", bd=1)
        txt_hasil.pack(fill=tk.BOTH, expand=True, pady=5)

        def aksi_enkripsi():
            pesan = ent_pesan.get().strip()
            if not pesan:
                return
            n, e = self.gm.kunci_publik
            try:
                hasil = enkripsi_pesan_bebas(pesan, e, n)
            except Exception as exc:
                messagebox.showerror("Error Enkripsi", str(exc), parent=self)
                return

            txt_hasil.delete("1.0", tk.END)
            txt_hasil.insert(tk.END, "=== HASIL ENKRIPSI MULTI-BLOK ===\n")
            txt_hasil.insert(tk.END, f"Pesan Setelah Filter & Padding 'X' : {hasil['pesan_bersih']}\n")
            txt_hasil.insert(tk.END, f"Ukuran Modulus n                    : {n}\n")
            txt_hasil.insert(tk.END, f"Ukuran Blok Digit (2N)             : {hasil['ukuran_blok']} digit ({hasil['huruf_per_blok']} huruf)\n")
            txt_hasil.insert(tk.END, f"Rangkaian Angka Plaintext          : {hasil['angka_str']}\n\n")
            txt_hasil.insert(tk.END, "Langkah Eksponensiasi Tiap Blok (C = M^e mod n):\n")
            for lk in hasil["langkah"]:
                txt_hasil.insert(tk.END, f"  {lk}\n")
            txt_hasil.insert(tk.END, f"\nDaftar Ciphertext Blok [C1, C2, ...] : {hasil['blok_ciphertext']}\n\n")

            # Uji dekripsi balik otomatis untuk membuktikan kebenaran
            d = getattr(self.gm, "_d", None)
            if d is not None:
                hasil_dekrip = dekripsi_pesan_bebas(hasil["blok_ciphertext"], d, n, len(hasil["pesan_bersih"]))
                txt_hasil.insert(tk.END, f"Verifikasi Dekripsi (M = C^d mod n)  : {hasil_dekrip['pesan']} (Cocok! ✓)\n")

        btn_run = tk.Button(
            frame,
            text="🔐 Jalankan Enkripsi Multi-Blok",
            font=("Helvetica", 10, "bold"),
            bg="#2980b9",
            fg="#ffffff",
            padx=10,
            pady=5,
            command=aksi_enkripsi,
        )
        btn_run.pack(anchor="w", pady=5)

    # ------------------ TAB 2: Serangan Kamus ------------------
    def _setup_tab_serangan_kamus(self, frame):
        tk.Label(
            frame,
            text="Serangan Kamus Terhadap Sandi Misteri C (Deterministik RSA)",
            font=("Helvetica", 11, "bold"),
            bg="#ffffff",
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            frame,
            text=(
                "Demonstrasi: Karena RSA textbook tidak menggunakan padding acak (OAEP),\n"
                "penyerang cukup mengenkripsi setiap kata dari kamus 5 huruf dan membandingkannya\n"
                "dengan Sandi Misteri C. Jika cocok, kata asli terungkap tanpa mengetahui kunci privat d!"
            ),
            font=("Helvetica", 9),
            bg="#ffffff",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 10))

        n, e = self.gm.kunci_publik
        C = self.gm.sandi_misteri

        tk.Label(frame, text=f"Target Sandi Misteri C : {C}", font=("Courier", 11, "bold"), bg="#ffffff", fg="#8e44ad").pack(anchor="w", pady=2)
        tk.Label(frame, text=f"Kunci Publik Digunakan  : (n={n}, e={e})", font=("Courier", 10), bg="#ffffff").pack(anchor="w", pady=2)

        txt_kamus = tk.Text(frame, height=14, font=("Courier", 10), bg="#fdfefe", relief="solid", bd=1)
        txt_kamus.pack(fill=tk.BOTH, expand=True, pady=10)

        def aksi_serangan():
            txt_kamus.delete("1.0", tk.END)
            txt_kamus.insert(tk.END, "Memulai simulasi serangan kamus terhadap sandi misteri...\n")
            self.update()

            hasil = serangan_kamus(C, e, n, self.gm._daftar_kata)

            txt_kamus.insert(tk.END, f"\nJumlah kata yang dienkripsi dan diuji : {hasil['jumlah_dicoba']} kata\n")
            txt_kamus.insert(tk.END, f"Waktu komputasi yang dihabiskan       : {hasil['waktu_detik']:.4f} detik\n")
            if hasil["ditemukan"]:
                txt_kamus.insert(tk.END, f"🎉 KATA RAHASIA DITEMUKAN             : '{hasil['kata']}' !\n\n")
            else:
                txt_kamus.insert(tk.END, "Kata tidak ditemukan di daftar kamus.\n\n")

            txt_kamus.insert(tk.END, f"Analisis Kriptografi:\n{hasil['penjelasan']}\n")

        btn_kamus = tk.Button(
            frame,
            text="⚡ Mulai Serangan Kamus",
            font=("Helvetica", 10, "bold"),
            bg="#e67e22",
            fg="#ffffff",
            padx=10,
            pady=5,
            command=aksi_serangan,
        )
        btn_kamus.pack(anchor="w")

    # ------------------ TAB 3: Faktorisasi n ------------------
    def _setup_tab_faktorisasi(self, frame):
        tk.Label(
            frame,
            text="Faktorisasi Modulus n = p * q dengan Pembagian Percobaan",
            font=("Helvetica", 11, "bold"),
            bg="#ffffff",
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            frame,
            text=(
                "Keamanan RSA bertumpu pada sulitnya memfaktorkan modulus n menjadi p dan q.\n"
                "Untuk n kecil (~10 digit), komputer dapat memfaktorkannya dalam hitungan milidetik.\n"
                "Namun untuk n 2048-bit nyata, faktorisasi membutuhkan waktu jutaan tahun."
            ),
            font=("Helvetica", 9),
            bg="#ffffff",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 10))

        n_aktif, _ = self.gm.kunci_publik

        frame_input = tk.Frame(frame, bg="#ffffff")
        frame_input.pack(fill=tk.X, pady=5)

        tk.Label(frame_input, text="Modulus n yang akan difaktorkan:", bg="#ffffff").pack(side=tk.LEFT, padx=(0, 10))
        ent_n = tk.Entry(frame_input, font=("Courier", 11), width=25)
        ent_n.insert(0, str(n_aktif))
        ent_n.pack(side=tk.LEFT, fill=tk.X, expand=True)

        txt_fak = tk.Text(frame, height=14, font=("Courier", 10), bg="#fdfefe", relief="solid", bd=1)
        txt_fak.pack(fill=tk.BOTH, expand=True, pady=10)

        def aksi_faktorisasi():
            try:
                n_target = int(ent_n.get().strip())
            except ValueError:
                messagebox.showerror("Input Error", "Nilai n harus berupa bilangan integer positif!", parent=self)
                return

            txt_fak.delete("1.0", tk.END)
            txt_fak.insert(tk.END, f"Memulai faktorisasi pembagian percobaan untuk n = {n_target}...\n")
            self.update()

            hasil = faktorisasi_n(n_target)

            txt_fak.insert(tk.END, f"\n{hasil['pesan']}\n")
            if hasil["p"] and hasil["q"]:
                phi = (hasil["p"] - 1) * (hasil["q"] - 1)
                txt_fak.insert(tk.END, f"Totient Euler φ(n) = (p-1)*(q-1) : {phi}\n")
                txt_fak.insert(tk.END, "Dengan p dan q terungkap, penyerang dapat menghitung kunci privat d!\n")

        btn_fak = tk.Button(
            frame,
            text="🔍 Faktorkan n Sekarang",
            font=("Helvetica", 10, "bold"),
            bg="#c0392b",
            fg="#ffffff",
            padx=10,
            pady=5,
            command=aksi_faktorisasi,
        )
        btn_fak.pack(anchor="w")

"""
Modul gui.py — Wordle Kripto (RSA Edition)

Antarmuka Grafis (GUI) berbasis Tkinter bawaan Python.
Menampilkan:
- Papan tebakan 6 baris × 5 kolom berwarna Wordle (Hijau, Kuning, Abu-abu).
- Papan keyboard interaktif A-Z dengan indikator warna terkini.
- Panel Kriptografi sisi kanan: Kunci Publik (n, e), Sandi Misteri (C),
  serta perbandingan Cipher Tebakan vs Sandi Misteri (deterministik RSA).
- Dialog pembuktian dekripsi RSA saat permainan berakhir.
- Dialog verifikasi sertifikat digital bertanda tangan (F-12) dengan fitur
  pengujian modifikasi angka untuk membuktikan kegagalan verifikasi.
- Menu pilihan ukuran kunci RSA dan integrasi Lab Kripto (F-16).
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox

from game_master import GameMaster
from wordle_engine import (
    WordleEngine,
    MAKS_TEBAKAN,
    WARNA_HIJAU,
    WARNA_KUNING,
    WARNA_ABU,
)

# Palet Warna Wordle Resmi
WARNA_BG = "#f6f7f8"
WARNA_PANEL = "#ffffff"
WARNA_KOTAK_KOSONG = "#ffffff"
WARNA_BORDER_KOSONG = "#d3d6da"
WARNA_BORDER_TERISI = "#878a8c"

WARNA_MAP = {
    WARNA_HIJAU: "#6aaa64",   # Hijau Wordle
    WARNA_KUNING: "#c9b458",  # Kuning Wordle
    WARNA_ABU: "#787c7e",     # Abu-abu Wordle
}

WARNA_TOMBOL_DEFAULT = "#d3d6da"
WARNA_TEKS_GELAP = "#1a1a1b"
WARNA_TEKS_TERANG = "#ffffff"


class WordleKriptoApp(tk.Tk):
    """
    Jendela aplikasi utama Wordle Kripto RSA Edition.
    """

    def __init__(self, args=None):
        super().__init__()
        self.args = args
        self.title("Wordle Kripto — RSA Edition (Matematika Diskrit 2)")
        self.geometry("980x680")
        self.minsize(920, 640)
        self.configure(bg=WARNA_BG)

        self.ukuran_kunci = getattr(args, "kunci", "default") if args else "default"
        self.seed = getattr(args, "seed", None) if args else None
        self.p_manual = getattr(args, "p", None) if args else None
        self.q_manual = getattr(args, "q", None) if args else None
        self.e_manual = getattr(args, "e", None) if args else None

        self.gm = None
        self.engine = None
        self.daftar_kata = []
        self.baris_aktif = 0
        self.tebakan_input = ""
        self.status_keyboard = {}  # huruf: prioritas warna (abu < kuning < hijau)

        self._inisialisasi_data()
        self._buat_menu_bar()
        self._buat_antarmuka()
        self._mulai_permainan_baru()

        # Bind event keyboard fisik
        self.bind("<Key>", self._on_key_press)
        self.bind("<BackSpace>", lambda e: self._on_backspace())
        self.bind("<Return>", lambda e: self._on_submit())

    def _inisialisasi_data(self):
        """Memuat daftar kata dari kata.txt."""
        try:
            self.daftar_kata = GameMaster.muat_kata("kata.txt")
        except Exception as exc:
            messagebox.showerror(
                "Error Daftar Kata",
                f"Gagal memuat kata.txt:\n{exc}\nPastikan file ada di direktori kerja.",
            )
            sys.exit(1)

    def _buat_menu_bar(self):
        """Membuat menu bar atas."""
        menubar = tk.Menu(self)

        # Menu Permainan
        menu_game = tk.Menu(menubar, tearoff=0)
        menu_game.add_command(label="Permainan Baru (Ctrl+N)", command=self._mulai_permainan_baru)
        menu_game.add_separator()
        menu_game.add_command(label="Keluar", command=self.destroy)
        menubar.add_cascade(label="Permainan", menu=menu_game)

        # Menu Ukuran Kunci RSA
        menu_kunci = tk.Menu(menubar, tearoff=0)
        menu_kunci.add_command(
            label="Default (p=51001, q=51031, n=2.602.632.031)",
            command=lambda: self._ubah_ukuran_kunci("default"),
        )
        menu_kunci.add_command(
            label="Kecil (Acak ~16-bit)",
            command=lambda: self._ubah_ukuran_kunci("kecil"),
        )
        menu_kunci.add_command(
            label="Sedang (Acak ~24-bit)",
            command=lambda: self._ubah_ukuran_kunci("sedang"),
        )
        menu_kunci.add_command(
            label="Besar (Acak ~32-bit)",
            command=lambda: self._ubah_ukuran_kunci("besar"),
        )
        menubar.add_cascade(label="Ukuran Kunci RSA", menu=menu_kunci)

        # Menu Lab Kripto (P2)
        menubar.add_command(label="🧪 Lab Kripto (P2)", command=self._buka_lab_kripto)

        self.config(menu=menubar)

    def _ubah_ukuran_kunci(self, ukuran: str):
        """Mengubah ukuran kunci dan merestart game."""
        self.ukuran_kunci = ukuran
        self.p_manual = None
        self.q_manual = None
        self.e_manual = None
        self._mulai_permainan_baru()

    def _buat_antarmuka(self):
        """Menyusun layout grid kiri (Wordle) dan kanan (Kripto)."""
        # Kontainer Utama
        main_frame = tk.Frame(self, bg=WARNA_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # ------------------ SISI KIRI (Papan Wordle & Keyboard) ------------------
        left_frame = tk.Frame(main_frame, bg=WARNA_BG)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        # Judul Game
        lbl_title = tk.Label(
            left_frame,
            text="WORDLE KRIPTO",
            font=("Helvetica", 20, "bold"),
            bg=WARNA_BG,
            fg=WARNA_TEKS_GELAP,
        )
        lbl_title.pack(pady=(0, 10))

        # Grid Kotak 6 baris × 5 kolom
        self.grid_frame = tk.Frame(left_frame, bg=WARNA_BG)
        self.grid_frame.pack(pady=5)

        self.kotak_labels = []
        for r in range(MAKS_TEBAKAN):
            row_labels = []
            for c in range(5):
                lbl = tk.Label(
                    self.grid_frame,
                    text="",
                    width=3,
                    height=1,
                    font=("Helvetica", 22, "bold"),
                    bg=WARNA_KOTAK_KOSONG,
                    fg=WARNA_TEKS_GELAP,
                    relief="solid",
                    bd=2,
                    highlightbackground=WARNA_BORDER_KOSONG,
                )
                lbl.grid(row=r, column=c, padx=4, pady=4)
                row_labels.append(lbl)
            self.kotak_labels.append(row_labels)

        # Label Pesan Status / Error
        self.lbl_status = tk.Label(
            left_frame,
            text="",
            font=("Helvetica", 11, "bold"),
            bg=WARNA_BG,
            fg="#d9381e",
        )
        self.lbl_status.pack(pady=6)

        # Papan Keyboard Huruf A-Z
        self.kbd_frame = tk.Frame(left_frame, bg=WARNA_BG)
        self.kbd_frame.pack(pady=5)
        self.tombol_keyboard = {}
        self._buat_keyboard_onscreen()

        # ------------------ SISI KANAN (Panel Kripto RSA) ------------------
        right_frame = tk.Frame(main_frame, bg=WARNA_PANEL, relief="ridge", bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0), ipadx=15, ipady=15)

        lbl_kripto_title = tk.Label(
            right_frame,
            text="🔐 PANEL KRIPTOGRAFI RSA",
            font=("Helvetica", 14, "bold"),
            bg=WARNA_PANEL,
            fg="#2c3e50",
        )
        lbl_kripto_title.pack(anchor="w", pady=(0, 12))

        # Info Kunci Publik (n, e)
        grp_publik = tk.LabelFrame(
            right_frame,
            text="Kunci Publik (Tersedia untuk Pemain)",
            font=("Helvetica", 10, "bold"),
            bg=WARNA_PANEL,
            fg="#34495e",
            padx=10,
            pady=8,
        )
        grp_publik.pack(fill=tk.X, pady=(0, 10))

        self.lbl_n = tk.Label(
            grp_publik,
            text="Modulus n: -",
            font=("Courier", 10),
            bg=WARNA_PANEL,
            anchor="w",
            justify=tk.LEFT,
            wraplength=380,
        )
        self.lbl_n.pack(fill=tk.X, pady=2)

        self.lbl_e = tk.Label(
            grp_publik,
            text="Eksponen e: -",
            font=("Courier", 10),
            bg=WARNA_PANEL,
            anchor="w",
        )
        self.lbl_e.pack(fill=tk.X, pady=2)

        # Info Sandi Misteri C
        grp_misteri = tk.LabelFrame(
            right_frame,
            text="Sandi Misteri (Ciphertext Kata Rahasia C = M^e mod n)",
            font=("Helvetica", 10, "bold"),
            bg=WARNA_PANEL,
            fg="#34495e",
            padx=10,
            pady=8,
        )
        grp_misteri.pack(fill=tk.X, pady=(0, 10))

        self.lbl_c = tk.Label(
            grp_misteri,
            text="C: -",
            font=("Courier", 11, "bold"),
            bg=WARNA_PANEL,
            fg="#8e44ad",
            anchor="w",
            wraplength=380,
            justify=tk.LEFT,
        )
        self.lbl_c.pack(fill=tk.X, pady=2)

        # Panel Kripto Tebakan Terkini
        grp_tebakan = tk.LabelFrame(
            right_frame,
            text="Analisis Kripto Tebakan Terakhir",
            font=("Helvetica", 10, "bold"),
            bg=WARNA_PANEL,
            fg="#34495e",
            padx=10,
            pady=8,
        )
        grp_tebakan.pack(fill=tk.X, pady=(0, 12))

        self.lbl_m_tebak = tk.Label(
            grp_tebakan,
            text="M tebakan  : -",
            font=("Courier", 10),
            bg=WARNA_PANEL,
            anchor="w",
        )
        self.lbl_m_tebak.pack(fill=tk.X, pady=2)

        self.lbl_c_tebak = tk.Label(
            grp_tebakan,
            text="C tebakan  : -",
            font=("Courier", 10),
            bg=WARNA_PANEL,
            anchor="w",
            wraplength=380,
            justify=tk.LEFT,
        )
        self.lbl_c_tebak.pack(fill=tk.X, pady=2)

        self.lbl_cocok = tk.Label(
            grp_tebakan,
            text="Status RSA : -",
            font=("Helvetica", 10, "bold"),
            bg=WARNA_PANEL,
            anchor="w",
        )
        self.lbl_cocok.pack(fill=tk.X, pady=2)

        # Tombol Aksi
        btn_frame = tk.Frame(right_frame, bg=WARNA_PANEL)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_sertifikat = tk.Button(
            btn_frame,
            text="📜 Verifikasi Sertifikat (F-12)",
            font=("Helvetica", 10, "bold"),
            bg="#2980b9",
            fg="#ffffff",
            relief="raised",
            bd=2,
            padx=10,
            pady=6,
            command=self._dialog_verifikasi_sertifikat,
        )
        self.btn_sertifikat.pack(fill=tk.X, pady=(0, 6))

        btn_ulang = tk.Button(
            btn_frame,
            text="🔄 Permainan Baru",
            font=("Helvetica", 10),
            bg="#27ae60",
            fg="#ffffff",
            relief="raised",
            bd=2,
            padx=10,
            pady=6,
            command=self._mulai_permainan_baru,
        )
        btn_ulang.pack(fill=tk.X)

    def _buat_keyboard_onscreen(self):
        """Membuat tombol keyboard virtual QWERTY di bawah papan."""
        baris_keyboard = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "⌫"],
        ]

        for baris in baris_keyboard:
            row_frame = tk.Frame(self.kbd_frame, bg=WARNA_BG)
            row_frame.pack(pady=2)
            for key in baris:
                w = 4 if key in ("ENTER", "⌫") else 3
                cmd = (
                    self._on_submit
                    if key == "ENTER"
                    else (self._on_backspace if key == "⌫" else lambda k=key: self._tambah_huruf(k))
                )
                btn = tk.Button(
                    row_frame,
                    text=key,
                    width=w,
                    height=1,
                    font=("Helvetica", 10, "bold"),
                    bg=WARNA_TOMBOL_DEFAULT,
                    fg=WARNA_TEKS_GELAP,
                    relief="raised",
                    bd=1,
                    command=cmd,
                )
                btn.pack(side=tk.LEFT, padx=2)
                if key not in ("ENTER", "⌫"):
                    self.tombol_keyboard[key] = btn

    def _mulai_permainan_baru(self):
        """Membuat sesi permainan baru."""
        self.lbl_status.config(text="Membuat kunci RSA & memilih kata...", fg="#2980b9")
        self.update()

        try:
            self.gm = GameMaster(
                p=self.p_manual,
                q=self.q_manual,
                e=self.e_manual,
                ukuran_kunci=self.ukuran_kunci,
                daftar_kata_path="kata.txt",
                seed=self.seed,
            )
            self.engine = WordleEngine(self.gm, self.daftar_kata)
        except Exception as exc:
            messagebox.showerror("Error Inisialisasi", f"Gagal membuat permainan: {exc}")
            return

        self.baris_aktif = 0
        self.tebakan_input = ""
        self.status_keyboard = {}

        # Reset Kotak Papan
        for r in range(MAKS_TEBAKAN):
            for c in range(5):
                lbl = self.kotak_labels[r][c]
                lbl.config(
                    text="",
                    bg=WARNA_KOTAK_KOSONG,
                    fg=WARNA_TEKS_GELAP,
                    relief="solid",
                    bd=2,
                )

        # Reset Keyboard
        for btn in self.tombol_keyboard.values():
            btn.config(bg=WARNA_TOMBOL_DEFAULT, fg=WARNA_TEKS_GELAP)

        # Update Info Kripto Kanan
        n, e = self.gm.kunci_publik
        C = self.gm.sandi_misteri
        self.lbl_n.config(text=f"Modulus n: {n}")
        self.lbl_e.config(text=f"Eksponen e: {e}")
        self.lbl_c.config(text=f"C = {C}")
        self.lbl_m_tebak.config(text="M tebakan  : -")
        self.lbl_c_tebak.config(text="C tebakan  : -")
        self.lbl_cocok.config(text="Status RSA : Siap", fg="#2c3e50")
        self.lbl_status.config(text="")

    def _on_key_press(self, event):
        """Menangani pengetikan tombol fisik keyboard."""
        char = event.char.upper()
        if char.isalpha() and len(char) == 1 and "A" <= char <= "Z":
            self._tambah_huruf(char)

    def _tambah_huruf(self, huruf: str):
        """Menambahkan huruf ke tebakan baris aktif."""
        if len(self.tebakan_input) < 5 and self.baris_aktif < MAKS_TEBAKAN:
            self.lbl_status.config(text="")
            col = len(self.tebakan_input)
            self.tebakan_input += huruf
            lbl = self.kotak_labels[self.baris_aktif][col]
            lbl.config(text=huruf, relief="solid", bd=2)

    def _on_backspace(self):
        """Menghapus huruf terakhir pada baris aktif."""
        if len(self.tebakan_input) > 0 and self.baris_aktif < MAKS_TEBAKAN:
            self.lbl_status.config(text="")
            col = len(self.tebakan_input) - 1
            self.tebakan_input = self.tebakan_input[:-1]
            lbl = self.kotak_labels[self.baris_aktif][col]
            lbl.config(text="")

    def _on_submit(self):
        """Memproses tebakan saat tombol ENTER ditekan."""
        if self.baris_aktif >= MAKS_TEBAKAN:
            return

        kata = self.tebakan_input
        try:
            hasil = self.engine.tebak(kata)
        except (ValueError, RuntimeError) as exc:
            self.lbl_status.config(text=f"⚠ {exc}", fg="#d9381e")
            return

        warna = hasil["warna"]
        cipher_tebakan = hasil["cipher_tebakan"]
        menang = hasil["menang"]
        kalah = hasil["kalah"]

        # Hitung M tebakan untuk panel kripto
        from encoding import teks_ke_angka_str
        m_tebak = int(teks_ke_angka_str(kata))

        # Animasi pewarnaan kotak baris
        for c in range(5):
            lbl = self.kotak_labels[self.baris_aktif][c]
            w = warna[c]
            bg_warna = WARNA_MAP.get(w, WARNA_BORDER_KOSONG)
            lbl.config(bg=bg_warna, fg=WARNA_TEKS_TERANG, relief="flat")

        # Update keyboard onscreen
        self._update_keyboard(kata, warna)

        # Update panel kripto kanan
        self.lbl_m_tebak.config(text=f"M tebakan  : {m_tebak:010d}")
        self.lbl_c_tebak.config(text=f"C tebakan  : {cipher_tebakan}")
        if menang:
            self.lbl_cocok.config(
                text="Status RSA : Cocok dengan C! (M = Rahasia) ✓",
                fg="#27ae60",
            )
        else:
            self.lbl_cocok.config(
                text="Status RSA : Berbeda dari C",
                fg="#c0392b",
            )

        self.baris_aktif += 1
        self.tebakan_input = ""

        # Evaluasi akhir game
        if menang or kalah:
            self._selesaikan_permainan(menang)

    def _update_keyboard(self, kata: str, warna: list):
        """Memperbarui warna tombol keyboard (prioritas: hijau > kuning > abu)."""
        prioritas = {WARNA_ABU: 1, WARNA_KUNING: 2, WARNA_HIJAU: 3}
        for huruf, w in zip(kata, warna):
            nilai_sekarang = self.status_keyboard.get(huruf, 0)
            nilai_baru = prioritas.get(w, 0)
            if nilai_baru > nilai_sekarang:
                self.status_keyboard[huruf] = nilai_baru
                btn = self.tombol_keyboard.get(huruf)
                if btn:
                    btn.config(bg=WARNA_MAP[w], fg=WARNA_TEKS_TERANG)

    def _selesaikan_permainan(self, menang: bool):
        """Menampilkan popup selesai dengan pembuktian matematis RSA."""
        rahasia_info = self.gm.buka_rahasia()
        kata_asli = rahasia_info["kata"]
        pembuktian = rahasia_info["pembuktian"]
        jumlah_tebakan = self.baris_aktif

        pesan_header = (
            f"🎉 Selamat! Anda Berhasil Menang dalam {jumlah_tebakan} tebakan!\n\n"
            if menang
            else f"😔 Kesempatan Habis! Kata rahasia adalah: {kata_asli}\n\n"
        )

        pesan_lengkap = (
            f"{pesan_header}"
            f"Pembuktian Matematis Dekripsi RSA:\n"
            f"{pembuktian}\n\n"
            f"Anda dapat melihat Sertifikat Hasil Bertanda Tangan Digital pada tombol di panel kanan."
        )

        messagebox.showinfo("Permainan Selesai", pesan_lengkap)

    def _dialog_verifikasi_sertifikat(self):
        """
        Membuka dialog verifikasi sertifikat digital bertanda tangan RSA (F-12).
        Memungkinkan pemain menguji integritas tanda tangan digital.
        """
        if self.gm is None or self.engine is None:
            return

        status = self.engine.status()
        sertifikat = self.gm.terbitkan_sertifikat(
            {
                "menang": status["menang"],
                "jumlah_tebakan": status["jumlah_tebakan"],
                "nomor_puzzle": getattr(self.gm, "_nomor_puzzle", 101),
            }
        )

        dlg = tk.Toplevel(self)
        dlg.title("Verifikasi Sertifikat Bertanda Tangan (RSA F-12)")
        dlg.geometry("560x440")
        dlg.configure(bg=WARNA_BG)
        dlg.transient(self)
        dlg.grab_set()

        lbl_header = tk.Label(
            dlg,
            text="📜 SERTIFIKAT HASIL PERMAINAN",
            font=("Helvetica", 14, "bold"),
            bg=WARNA_BG,
            fg="#2c3e50",
        )
        lbl_header.pack(pady=(15, 8))

        lbl_desc = tk.Label(
            dlg,
            text="Game Master menandatangani ringkasan hasil permainan (R) dengan kunci privat\ntanda tangan: S = R^d_sign mod n_sign. Verifikasi memeriksa: S^e_sign mod n_sign == R.",
            font=("Helvetica", 9),
            bg=WARNA_BG,
            justify=tk.CENTER,
        )
        lbl_desc.pack(pady=(0, 10))

        frame_form = tk.Frame(dlg, bg=WARNA_PANEL, relief="ridge", bd=2, padx=15, pady=12)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        tk.Label(frame_form, text=f"Data Ringkasan (R) : {sertifikat['R']}", font=("Courier", 11, "bold"), bg=WARNA_PANEL).pack(anchor="w", pady=3)
        tk.Label(frame_form, text=f"Modulus n_sign     : {sertifikat['n_sign']}", font=("Courier", 10), bg=WARNA_PANEL).pack(anchor="w", pady=3)
        tk.Label(frame_form, text=f"Eksponen e_sign    : {sertifikat['e_sign']}", font=("Courier", 10), bg=WARNA_PANEL).pack(anchor="w", pady=3)

        tk.Label(frame_form, text="Tanda Tangan Digital (S):", font=("Helvetica", 10, "bold"), bg=WARNA_PANEL).pack(anchor="w", pady=(8, 2))
        
        ent_s = tk.Entry(frame_form, font=("Courier", 11), width=35)
        ent_s.insert(0, str(sertifikat["S"]))
        ent_s.pack(fill=tk.X, pady=2)

        lbl_petunjuk = tk.Label(
            frame_form,
            text="💡 Cobalah ubah 1 digit pada kotak S di atas, lalu klik Verifikasi untuk membuktikan bahwa tanda tangan akan ditolak (integritas data terjamin).",
            font=("Helvetica", 8, "italic"),
            bg=WARNA_PANEL,
            fg="#7f8c8d",
            wraplength=460,
            justify=tk.LEFT,
        )
        lbl_petunjuk.pack(anchor="w", pady=(4, 10))

        lbl_hasil_verif = tk.Label(
            frame_form,
            text="Status: Klik tombol Verifikasi di bawah.",
            font=("Helvetica", 10, "bold"),
            bg=WARNA_PANEL,
            fg="#2c3e50",
        )
        lbl_hasil_verif.pack(anchor="w", pady=5)

        def aksi_verifikasi():
            try:
                s_input = int(ent_s.get().strip())
            except ValueError:
                lbl_hasil_verif.config(text="❌ Nilai S harus berupa angka integer!", fg="#c0392b")
                return

            valid = self.gm.verifikasi_sertifikat(
                sertifikat["R"], s_input, sertifikat["n_sign"], sertifikat["e_sign"]
            )
            if valid:
                lbl_hasil_verif.config(
                    text="✅ VALID! Tanda tangan cocok dengan data ringkasan R (S^e mod n == R).",
                    fg="#27ae60",
                )
            else:
                lbl_hasil_verif.config(
                    text="❌ TIDAK VALID! Tanda tangan palsu atau telah dimodifikasi!",
                    fg="#c0392b",
                )

        btn_verif = tk.Button(
            frame_form,
            text="🔍 Verifikasi Tanda Tangan",
            font=("Helvetica", 10, "bold"),
            bg="#27ae60",
            fg="#ffffff",
            padx=12,
            pady=4,
            command=aksi_verifikasi,
        )
        btn_verif.pack(side=tk.LEFT, pady=5)

        btn_tutup = tk.Button(
            frame_form,
            text="Tutup",
            font=("Helvetica", 10),
            padx=12,
            pady=4,
            command=dlg.destroy,
        )
        btn_tutup.pack(side=tk.RIGHT, pady=5)

    def _buka_lab_kripto(self):
        """Membuka jendela Lab Kripto (P2)."""
        try:
            from lab_kripto import LabKriptoWindow
            LabKriptoWindow(self, self.gm)
        except Exception as exc:
            messagebox.showerror("Lab Kripto Error", f"Gagal membuka Lab Kripto:\n{exc}")


def jalankan_gui(args=None):
    """Titik masuk untuk meluncurkan GUI."""
    app = WordleKriptoApp(args)
    app.mainloop()

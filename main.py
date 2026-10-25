"""
Wordle Kripto (RSA Edition) -- Titik masuk program.

Penggunaan:
    python main.py          # Buka GUI (default)
    python main.py --cli    # Mode CLI
    python main.py --cli --kunci kecil   # CLI dengan kunci acak kecil
    python main.py --cli --seed 42       # CLI dengan seed tetap
    python main.py --cli --p 43 --q 59 --e 13  # CLI dengan kunci manual
"""
import argparse
import sys
import os

# Konfigurasi stdout ke UTF-8 jika berjalan di terminal Windows yang menggunakan cp1252/cp437
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass


# ---------------------------------------------------------------------------
# Konstanta warna emoji
# ---------------------------------------------------------------------------
EMOJI_WARNA = {
    'hijau': '\U0001f7e9',
    'kuning': '\U0001f7e8',
    'abu': '\u2b1b',
}

HEADER = """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551       WORDLE KRIPTO (RSA Edition)    \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d"""


# ---------------------------------------------------------------------------
# Fungsi utilitas
# ---------------------------------------------------------------------------

def muat_kata(path: str = 'kata.txt') -> list:
    """
    Baca kata.txt, satu per baris, filter 5 huruf A-Z, kembalikan list kapital.

    Parameters
    ----------
    path : str
        Lokasi file daftar kata.

    Returns
    -------
    list[str]
        Daftar kata valid (5 huruf, huruf kapital).

    Raises
    ------
    SystemExit
        Jika file tidak ditemukan.
    """
    abs_path = os.path.abspath(path)
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            baris_list = f.readlines()
    except FileNotFoundError:
        print(f"[ERROR] File daftar kata tidak ditemukan: '{abs_path}'")
        print("        Pastikan file 'kata.txt' ada di direktori yang sama dengan main.py,")
        print("        atau berikan path lengkap yang benar.")
        sys.exit(1)

    kata_valid = []
    for baris_kata in baris_list:
        kata = baris_kata.strip().upper()
        # Filter: tepat 5 huruf, hanya A-Z ASCII
        if len(kata) == 5 and kata.isalpha() and kata.isascii():
            kata_valid.append(kata)

    if not kata_valid:
        print(f"[ERROR] Tidak ada kata 5-huruf valid di '{abs_path}'.")
        sys.exit(1)

    return kata_valid


# ---------------------------------------------------------------------------
# Mode CLI — helper display
# ---------------------------------------------------------------------------

def _tampilkan_header(n: int, e: int, C: int) -> None:
    """Tampilkan header permainan beserta informasi kunci publik."""
    print(HEADER)
    print(f"Kunci publik (n, e) : ({n}, {e})")
    print(f"Sandi misteri (C)   : {C}")
    print()


def _tampilkan_baris_tebakan(kata: str, warna: list) -> None:
    """Tampilkan satu baris tebakan dengan emoji warna dan huruf."""
    emoji_row = ' '.join(EMOJI_WARNA.get(w, '\u2b1b') for w in warna)
    huruf_row = ' '.join(kata)
    print(f"  {emoji_row}   {huruf_row}")


def _tampilkan_panel_kripto(cipher_tebakan: int, sandi_misteri: int, menang: bool) -> None:
    """Tampilkan panel kripto setelah setiap tebakan."""
    status = 'sama dengan C! \u2713' if menang else 'berbeda dari C'
    print(f"  [kripto] Cipher tebakan = {cipher_tebakan} ({status})")


def _tampilkan_sertifikat(gm, menang: bool, jumlah_tebakan: int, nomor_puzzle: int) -> None:
    """Minta, tampilkan, dan verifikasi sertifikat dari GameMaster."""
    print()
    print("\u2500" * 42)
    print("  Membuat sertifikat...")
    try:
        sertifikat = gm.terbitkan_sertifikat({
            'menang': menang,
            'jumlah_tebakan': jumlah_tebakan,
            'nomor_puzzle': nomor_puzzle,
        })
    except Exception as exc:
        print(f"  [ERROR] Gagal membuat sertifikat: {exc}")
        print("\u2500" * 42)
        return

    R = sertifikat['R']
    S = sertifikat['S']
    n_sign = sertifikat['n_sign']
    e_sign = sertifikat['e_sign']

    print("  Sertifikat:")
    print(f"    R       = {R}")
    print(f"    S       = {S}")
    print(f"    n_sign  = {n_sign}")
    print(f"    e_sign  = {e_sign}")

    try:
        valid = gm.verifikasi_sertifikat(R, S, n_sign, e_sign)
    except Exception as exc:
        print(f"  [ERROR] Gagal verifikasi: {exc}")
        print("\u2500" * 42)
        return

    status_str = "\u2705 VALID" if valid else "\u274c TIDAK VALID"
    print(f"  Verifikasi : {status_str}")
    print("\u2500" * 42)


# ---------------------------------------------------------------------------
# Mode CLI — sesi utama
# ---------------------------------------------------------------------------

def jalankan_cli(args) -> None:
    """
    Sesi bermain Wordle di CLI.

    Parameters
    ----------
    args : argparse.Namespace
        Argumen hasil parsing: kunci, seed, p, q, e.
    """
    # Import modul permainan
    try:
        from game_master import GameMaster
        from wordle_engine import WordleEngine, MAKS_TEBAKAN
    except ImportError as exc:
        print(f"[ERROR] Gagal memuat modul permainan: {exc}")
        print("        Pastikan game_master.py dan wordle_engine.py ada di direktori yang sama.")
        sys.exit(1)

    nomor_puzzle = 0

    while True:
        nomor_puzzle += 1

        # 1. Muat daftar kata
        daftar_kata = muat_kata('kata.txt')

        # 2. Inisialisasi GameMaster
        try:
            gm = GameMaster(
                p=args.p,
                q=args.q,
                e=args.e,
                ukuran_kunci=args.kunci,
                daftar_kata_path='kata.txt',
                seed=args.seed,
            )
        except Exception as exc:
            print(f"[ERROR] Gagal menginisialisasi GameMaster: {exc}")
            sys.exit(1)

        n, e = gm.kunci_publik
        C = gm.sandi_misteri

        # 3. Inisialisasi WordleEngine
        try:
            engine = WordleEngine(gm, daftar_kata)
        except Exception as exc:
            print(f"[ERROR] Gagal menginisialisasi WordleEngine: {exc}")
            sys.exit(1)

        # 4. Tampilkan header
        _tampilkan_header(n, e, C)

        # 5. Loop tebakan
        menang = False

        while True:
            status = engine.status()
            if not status['aktif']:
                break

            tebakan_ke = status['jumlah_tebakan'] + 1

            try:
                masukan = input(f"Tebakan {tebakan_ke}/{MAKS_TEBAKAN} > ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\nPermainan diakhiri.")
                sys.exit(0)

            # Proses tebakan
            try:
                result = engine.tebak(masukan)
            except ValueError as exc:
                print(f"  \u26a0 {exc}")
                continue
            except RuntimeError as exc:
                print(f"  \u26a0 {exc}")
                break

            warna = result['warna']
            cipher_tebakan = result['cipher_tebakan']
            menang = result['menang']

            _tampilkan_baris_tebakan(masukan, warna)
            _tampilkan_panel_kripto(cipher_tebakan, C, menang)
            print()

            if menang or result.get('kalah', False):
                break

        # 6. Setelah selesai
        status_akhir = engine.status()
        jumlah_tebakan = status_akhir['jumlah_tebakan']

        try:
            rahasia = gm.buka_rahasia()
        except Exception as exc:
            rahasia = {'kata': '?????', 'pembuktian': f'(error: {exc})'}

        if menang:
            print(f"\U0001f389 Benar! Kata '{rahasia['kata']}' ditemukan dalam {jumlah_tebakan} tebakan!")
        else:
            print(f"\U0001f614 Sayang sekali. Kata rahasia adalah: {rahasia['kata']}")

        print()
        print("\u2500" * 42)
        print("  Pembuktian Dekripsi RSA:")
        print(f"  {rahasia.get('pembuktian', '(tidak tersedia)')}")
        print("\u2500" * 42)
        print()

        # 7. Menu setelah selesai
        while True:
            try:
                pilihan = input("[S]ertifikat | [U]lang | [K]eluar > ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\nSampai jumpa!")
                sys.exit(0)

            if pilihan == 'S':
                _tampilkan_sertifikat(gm, menang, jumlah_tebakan, nomor_puzzle)
                continue  # tanya lagi setelah tampilkan
            elif pilihan == 'U':
                if args.seed is not None:
                    print("  (Seed tetap sama -- puzzle akan sama)")
                break  # ulangi loop utama
            elif pilihan == 'K':
                print("Sampai jumpa!")
                sys.exit(0)
            else:
                print("  Pilihan tidak dikenal. Ketik S, U, atau K.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parsing argumen lalu pilih mode CLI atau GUI."""
    parser = argparse.ArgumentParser(
        description='Wordle Kripto RSA Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--cli', action='store_true', help='Jalankan mode CLI')
    parser.add_argument(
        '--kunci',
        choices=['default', 'kecil', 'sedang', 'besar'],
        default='default',
        help='Ukuran kunci RSA (default: default)',
    )
    parser.add_argument('--seed', type=int, default=None, help='Seed RNG untuk reproduksibilitas')
    parser.add_argument('--p', type=int, default=None, help='Bilangan prima p (kunci manual)')
    parser.add_argument('--q', type=int, default=None, help='Bilangan prima q (kunci manual)')
    parser.add_argument('--e', type=int, default=None, help='Eksponen publik e (kunci manual)')
    args = parser.parse_args()

    if args.cli:
        jalankan_cli(args)
    else:
        try:
            from gui import jalankan_gui
            jalankan_gui(args)
        except ImportError:
            print('GUI tidak tersedia. Menjalankan mode CLI...')
            jalankan_cli(args)


if __name__ == '__main__':
    main()

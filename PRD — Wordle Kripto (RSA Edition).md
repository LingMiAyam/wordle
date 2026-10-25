# PRD — Wordle Kripto (RSA Edition)

*Draf v0.2 · 25 Oktober 2026 · Dasar: ketentuan Projek Kelompok Matdis 2, materi Kriptografi (Bagian 4.6), dan kode RSA.py*

## 1. Ringkasan

Wordle Kripto adalah permainan tebak kata 5 huruf ala Wordle yang kata rahasianya tidak disimpan sebagai teks biasa, melainkan sebagai ciphertext RSA. Pemain melihat “sandi misteri” (angka hasil enkripsi) lalu menebak kata aslinya dalam 6 percobaan. Tujuan utamanya adalah mendemonstrasikan RSA persis seperti materi dosen (huruf diubah ke angka A=00 … Z=25, dipecah menjadi blok, dienkripsi dengan C = M^e mod n, didekripsi dengan M = C^d mod n) dalam bentuk yang interaktif. Luaran akhir proyek ada dua: program (dikumpulkan sebagai file .zip) dan makalah yang menjelaskan proyek, program, tampilannya, serta pemanfaatan aritmetika modular.

**Ketentuan projek dan dampaknya pada rancangan.** Ketentuan dari dosen sudah diterima dan diterapkan di seluruh PRD ini:

| Ketentuan | Dampak pada rancangan |
| --- | --- |
| Program RSA atau kriptografi, bahasa bebas | Wordle Kripto dalam Python; RSA menjadi inti gameplay |
| Tingkat kompleksitas program dinilai | Fitur P1 (GUI, kunci acak dengan Miller–Rabin, sertifikat bertanda tangan) dikerjakan lebih dulu, lalu P2 (Lab Kripto) bila waktu cukup |
| Library boleh, tetapi banyaknya dinilai | Hanya pustaka standar Python seperlunya; algoritma RSA ditulis sendiri; daftar library masuk makalah (bagian 9) |
| Makalah memuat penjelasan projek, program, dan tampilan | Kerangka makalah dan rencana tangkapan layar ada di bagian 11 |
| Aritmetika modular dijelaskan di makalah, bukan fitur program | Tidak ada fitur penjelasan modular di program; pemetaan operasi modular ke kode disiapkan sebagai bahan makalah (bagian 11) |
| Sampul memuat semua nama anggota; kontribusi tiap anggota ada di makalah | Tabel pembagian tugas diisi sejak awal (bagian 11) |
| Source code dikumpulkan sebagai .zip lewat Google Form oleh satu orang; deadline 29 Oktober 2026 | Jadwal disusun mundur dari tanggal itu, dengan kode dibekukan 28 Oktober (bagian 13) |
| Presentasi sebelum UAS bila memungkinkan | Skrip demo disiapkan sebagai item P2 (F-18) |

**Asumsi yang masih dipakai.**

- Seluruh kode dalam Python; fungsi inti dari RSA.py dirombak.
- Antarmuka utama berupa GUI Tkinter (bawaan Python); CLI tetap ada sebagai cadangan dan alat uji.
- Satu pemain, offline, tanpa server.
- Kata 5 huruf, hanya A–Z; daftar kata berupa berkas teks yang bisa diganti (default bahasa Indonesia).
- Jumlah anggota belum diketahui, jadi pembagian peran di bagian 11 bisa digabung atau dipecah.

## 2. Latar Belakang dan Tujuan

Materi dosen membahas sandi klasik (Caesar, shift, affine, transposisi), kriptosistem kunci publik, RSA, protokol kriptografi (Diffie-Hellman dan tanda tangan digital). Teman sudah membuat RSA.py, tetapi baru mencakup pembuatan kunci; belum ada fungsi enkripsi, dekripsi, maupun pengubah teks ke angka. Game ini menyatukan keduanya.

**Tujuan**

1. Memiliki alur RSA lengkap (kunci → enkripsi → dekripsi) yang hasilnya cocok dengan contoh di slide dosen, dengan algoritma inti ditulis sendiri.
2. Menjadikan RSA bagian inti gameplay, bukan tempelan.
3. Mencapai kompleksitas setinggi yang realistis dalam waktu sampai 29 Oktober 2026 (GUI, kunci acak, tanda tangan digital) tanpa mengorbankan kestabilan.
4. Menekan penggunaan library ke pustaka standar seperlunya.
5. Menghasilkan makalah yang selaras dengan program yang benar-benar berjalan.
6. Membuat kode mudah dijelaskan saat presentasi.

**Bukan tujuan**

- Keamanan nyata. Kunci berukuran kecil (±10 digit) bisa difaktorkan dalam sekejap, dan RSA di sini adalah versi “textbook” tanpa padding.
- Multiplayer, jaringan, atau papan skor online.
- Kunci 2048-bit, OAEP, atau pustaka kriptografi produksi.
- Fitur khusus yang menjelaskan aritmetika modular di dalam program; sesuai ketentuan, penjelasannya cukup di makalah.
- Versi web atau aplikasi seluler.

## 3. Pengguna dan Skenario

- **Pemain:** teman sekelas yang ingin bermain sambil belajar RSA.
- **Penilai:** dosen yang ingin melihat RSA benar-benar bekerja dan sesuai materi.

Skenario utama: pemain membuka game, melihat kunci publik dan sandi misteri, menebak kata hingga benar atau kehabisan percobaan, lalu game membuka kata asli dan menunjukkan bahwa dekripsi sandi misteri memang menghasilkan kata tersebut.

## 4. Konsep Permainan

### 4.1 Aturan dasar Wordle

- Pemain punya 6 tebakan untuk kata rahasia 5 huruf.
- Setelah tiap tebakan, setiap huruf diberi warna: **hijau** (huruf benar, posisi benar), **kuning** (huruf ada di kata tetapi posisi salah), **abu-abu** (huruf tidak ada).
- Huruf kembar ditangani dengan benar: hijau dihitung lebih dulu, lalu kuning hanya diberikan selama jumlah huruf itu di kata rahasia belum habis. Contoh: rahasia ABCDE, tebakan AAXXX → hanya A pertama yang hijau, A kedua abu-abu.
- Tebakan yang bukan 5 huruf atau tidak ada di daftar kata tidak dihitung sebagai percobaan.

### 4.2 Peran RSA dalam game

1. **Awal permainan.** Game membuat kunci RSA (n, e, d), memilih kata rahasia W secara acak, mengubahnya menjadi angka M, lalu menghitung C = M^e mod n.
2. **Layar pemain** hanya menampilkan kunci publik (n, e) dan sandi misteri C.
3. **Setiap tebakan G.** Game mengubah G menjadi angka dan mengenkripsinya dengan kunci publik. Hasilnya ditampilkan sebagai “cipher tebakan”. Tebakan benar jika cipher tebakan sama dengan C.
4. **Penilaian warna.** “Game Master” mendekripsi C dengan kunci privat d untuk mendapatkan W, lalu membandingkan huruf demi huruf.
5. **Akhir permainan.** Kata asli dibuka, dan game memperlihatkan pembuktian D(C) = W.

### 4.3 Batas tanggung jawab

Modul antarmuka (UI) hanya boleh menerima n, e, C, dan hasil warna. Kunci privat d dan kata rahasia hanya ada di modul Game Master sampai permainan selesai. Pemisahan ini yang membuat peran RSA bermakna: pemain memegang kunci publik dan ciphertext, sama seperti penyadap pada skenario kunci publik di materi.

Catatan jujur: karena semuanya berjalan dalam satu program, kata rahasia tetap ada di memori. Ini demonstrasi edukatif, bukan perlindungan sungguhan.

Celah yang perlu dibahas di makalah: RSA textbook bersifat deterministik dan kata rahasia hanya satu dari sejumlah kecil kata di daftar, sehingga siapa pun yang mengenkripsi seluruh daftar kata dengan kunci publik dapat menemukan kata yang cipherannya sama dengan C tanpa memfaktorkan n (serangan kamus). UI permainan tidak menyediakan fungsi itu; Lab Kripto (F-16) justru memperagakannya.

## 5. Kebutuhan Fungsional

Prioritas: **P0** wajib, **P1** penting, **P2** opsional.

- **F-01 (P0) Pembuatan kunci.** Menerima p, q, e; memvalidasi (p dan q prima, p ≠ q, 1 < e < φ, gcd(e, φ) = 1, n ≥ 2525252525 pada mode game); menghitung n = p·q, φ = (p−1)(q−1), dan d sebagai invers e modulo φ dengan algoritma Euclid yang diperluas. Menyediakan nilai default yang valid agar game bisa langsung jalan.
- **F-02 (P0) Encoding.** Mengubah teks ke angka dua digit per huruf (A=00 … Z=25), menggabungkannya, dan membaginya menjadi blok. Ukuran blok dihitung otomatis dari n sesuai aturan materi (lihat bagian 6). Decoding wajib mengisi nol di kiri (contoh: 0120130600).
- **F-03 (P0) Enkripsi.** C = M^e mod n untuk setiap blok, memakai eksponensiasi modular kuadrat-dan-kali yang ditulis sendiri.
- **F-04 (P0) Dekripsi.** M = C^d mod n untuk setiap blok, lalu decoding ke huruf.
- **F-05 (P0) Kata rahasia.** Memilih kata acak dari daftar kata, mengenkripsinya, dan hanya menampilkan C.
- **F-06 (P0) Input tebakan.** Huruf kapital otomatis, validasi 5 huruf A–Z, validasi ada di daftar kata.
- **F-07 (P0) Umpan balik warna** dengan penanganan huruf kembar (bagian 4.1).
- **F-08 (P0) Siklus permainan.** Maksimal 6 tebakan; pesan menang/kalah; kata asli dibuka di akhir; opsi main lagi.
- **F-09 (P0) Antarmuka CLI.** Prototipe yang memakai seluruh fitur P0 dan tetap dipertahankan sebagai cadangan jika GUI belum selesai.
- **F-10 (P1) GUI Tkinter.** Menu awal, papan 6×5 berwarna, papan huruf, kolom sandi misteri dan kunci publik, serta pesan menang atau kalah. Tangkapan layarnya menjadi bahan makalah.
- **F-11 (P1) Kunci acak dengan ukuran pilihan.** Membuat bilangan prima acak dengan uji Miller–Rabin yang ditulis sendiri (tes primalitas probabilistik di materi); pemain memilih ukuran kunci (kecil, sedang, besar) dan n selalu memenuhi syarat blok.
- **F-12 (P1) Sertifikat hasil bertanda tangan.** Setelah game selesai, Game Master menandatangani ringkasan hasil (nomor puzzle, menang atau kalah, jumlah tebakan) yang dikodekan sebagai satu angka R lebih kecil dari n, mengikuti protokol tanda tangan di slide: S = R^d mod n. Menu “Verifikasi sertifikat” memeriksa S^e mod n = R; sertifikat yang diubah satu angka harus gagal. Gunakan pasangan kunci tanda tangan yang terpisah dari kunci enkripsi game: jika kunci yang sama dipakai, menandatangani C sama saja dengan mendekripsinya dan membuka kata rahasia.
- **F-13 (P1) Panel kripto.** Opsi (bisa dimatikan) yang menampilkan angka M dan cipher tebakan di samping hasil warna, dengan catatan bahwa tebakan benar menghasilkan cipher yang sama dengan C karena RSA textbook bersifat deterministik.
- **F-14 (P1) Papan huruf.** Status tiap huruf A–Z (belum dipakai, abu-abu, kuning, hijau).
- **F-15 (P1) Statistik sesi.** Jumlah menang dan kalah serta distribusi jumlah tebakan.
- **F-16 (P2) Lab Kripto.** Menu terpisah dari permainan yang memakai kunci aktif untuk (a) mengenkripsi dan mendekripsi pesan bebas lebih dari satu blok, dengan huruf X sebagai pengisi blok terakhir (pilihan tim), (b) serangan kamus terhadap sandi misteri, dan (c) faktorisasi n dengan pembagian percobaan beserta waktunya untuk berbagai ukuran kunci. Ini peragaan bahwa keamanan RSA bergantung pada sulitnya memfaktorkan n, bukan penjelasan aritmetika modular, sehingga sejalan dengan ketentuan.
- **F-17 (P2) Mode sandi klasik.** Petunjuk berupa kata yang dienkripsi dengan shift cipher (kunci k acak) yang harus didekripsi pemain.
- **F-18 (P2) Skrip demo presentasi.** Alur demo 3–5 menit dan kunci yang dipakai, disiapkan jika presentasi dilaksanakan sebelum UAS.

## 6. Spesifikasi Kriptografi

**Encoding.** A=00, B=01, …, Z=25. Kata 5 huruf menjadi string 10 digit, lalu dibaca sebagai bilangan bulat M. Contoh: BUNGA → 0120130600.

**Ukuran blok (aturan materi).** Blok terdiri dari 2N digit, di mana 2N adalah bilangan genap terbesar sehingga bilangan 2525…25 (2N digit) tidak melebihi n. Akibatnya, setiap blok M selalu lebih kecil dari n. Dua contoh:

- n = 2537 → 2525 ≤ 2537 < 252525, sehingga blok 4 digit (2 huruf).
- Agar satu kata 5 huruf muat dalam satu blok 10 digit, dibutuhkan 2525252525 ≤ n < 252525252525. Game wajib menolak kunci yang n-nya lebih kecil dari 2525252525.

**Parameter default untuk game.**

- p = 51001, q = 51031, e = 65537
- n = 2602632031, φ = 2602530000
- d = 154713473 (e·d mod φ = 1, gcd(e, φ) = 1)

Perlu diperhatikan: pasangan prima yang terlalu kecil (misalnya p = 50021, q = 50023) menghasilkan n = 2502200483 yang lebih kecil dari 2525252525, sehingga kata seperti ZZZZZ tidak bisa didekripsi dengan benar. Inilah alasan validasi n pada F-01.

**Enkripsi dan dekripsi.** C = M^e mod n dan M = C^d mod n. Hasil dekripsi diubah ke string 10 digit dengan pengisi nol di kiri sebelum di-decode.

**Algoritma yang ditulis sendiri (tanpa library).** (1) FPB dengan algoritma Euclid. (2) Invers modulo dengan algoritma Euclid yang diperluas (dasar fungsi cari\_d). (3) Eksponensiasi modular kuadrat-dan-kali, yang mereduksi modulo n di setiap langkah agar bilangan tidak membengkak. (4) Uji prima: pembagian percobaan untuk bilangan kecil dan Miller–Rabin untuk bilangan besar. (5) Pembuatan bilangan prima acak berukuran bit tertentu. Fungsi bawaan pow(a, b, n) hanya dipakai di berkas uji sebagai pembanding hasil. Pada kunci besar, kata 5 huruf tetap muat dalam satu blok karena M < n; pakai e = 65537 (bukan e kecil seperti 3) agar M^e melampaui n dan benar-benar tereduksi modulo n.

**Data uji dari materi dosen (n = 2537, e = 13, d = 937).**

- Enkripsi STOP: blok 1819 dan 1415 → 2081 dan 2182.
- Dekripsi 0981 0461 → 0704 1115 → HELP.
- Tanda tangan (untuk F-12): blok 1204, 0419, 0019, 1314, 1413 ditandatangani dengan d menjadi 0817, 0555, 1310, 2173, 1026, dan penerima mendapatkan kembali pesan MEET AT NOON.

**Data uji untuk game (parameter default di atas).**

- BUNGA → M = 0120130600 → C = 587403072 → dekripsi kembali BUNGA.
- BUKAN → C = 293955741.
- ZZZZZ → M = 2525252525 → enkripsi lalu dekripsi harus kembali ZZZZZ.

## 7. Evaluasi Kode RSA.py

Kode teman sudah mengerjakan sebagian inti (uji prima, hitung n, hitung d) tanpa memakai library sama sekali, sehingga sejalan dengan kebijakan library di bagian 9. Hasil pengujian dan tindakan yang dibutuhkan:

- **Bug yang membuat program gagal (P0).** Fungsi cek\_gcd didefinisikan dengan tiga parameter (p, q, e), tetapi dipanggil di dalam RSA() dengan dua argumen (phi, e). Akibatnya RSA(43, 59, 13) langsung berhenti dengan TypeError. *Tindakan:* jadikan cek\_gcd(a, b) umum untuk dua bilangan (atau pakai math.gcd) dan sesuaikan pemanggilnya.
- **cari\_d sudah benar.** cari\_d(13, 2436) menghasilkan 937, sama dengan contoh slide. Namun komentar di kode menyebut bagian ini belum sepenuhnya dipahami. *Tindakan:* tambahkan penjelasan singkat (algoritma Euclid yang diperluas mencari d sehingga e·d ≡ 1 mod φ) agar bisa dijelaskan saat demo.
- **Belum ada enkripsi, dekripsi, dan encoding (P0).** Ketiganya perlu ditambahkan (F-02 sampai F-04).
- **Validasi e kurang.** e = 0 menyebabkan ZeroDivisionError, dan e = 1 lolos validasi padahal membuat d = 1 sehingga ciphertext sama dengan plaintext. *Tindakan:* wajibkan 1 < e < φ.
- **Tidak ada pemeriksaan n untuk ukuran blok (P0).** Tambahkan syarat n ≥ 2525252525 pada mode game.
- **Keluaran lewat print dan return kosong saat gagal.** Sulit dipakai oleh modul game. *Tindakan:* ganti dengan exception yang jelas (misalnya ValueError dengan pesan Indonesia) dan fungsi yang mengembalikan nilai.
- **cek\_prima memakai pembagian percobaan.** Cukup untuk p dan q berukuran 5 digit, tetapi lambat untuk bilangan besar; Miller–Rabin dicatat sebagai F-11.

Pastikan juga anggota tim memahami bagian yang ditulis dengan bantuan AI dan mengikuti aturan mata kuliah mengenai penggunaan AI.

## 8. Arsitektur Modul

- **rsa\_core.py** — fpb, cari\_d (Euclid diperluas), eksponensiasi\_modular (kuadrat-dan-kali), cek\_prima, miller\_rabin, buat\_prima, buat\_kunci, enkripsi\_blok, dekripsi\_blok, tanda\_tangan, verifikasi (hasil refaktor RSA.py).
- **encoding.py** — teks ke angka, angka ke teks, hitung ukuran blok dari n, pembagian blok.
- **game\_master.py** — memegang kunci privat dan kata rahasia, mendekripsi C, menilai tebakan, menerbitkan sertifikat hasil, dan menjaga batas pada bagian 4.3.
- **wordle\_engine.py** — aturan 6 percobaan, validasi tebakan, algoritma warna dua tahap (hijau dahulu, lalu kuning).
- **kata.txt** — daftar kata 5 huruf, satu kata per baris.
- **gui.py** — antarmuka Tkinter: menu, papan 6×5, papan huruf, panel kripto, pilihan ukuran kunci, verifikasi sertifikat.
- **main.py** — titik masuk program; CLI sebagai cadangan dan alat uji (opsi --cli).
- **lab\_kripto.py** (P2) — pesan bebas, serangan kamus, faktorisasi.
- **tests/** — uji unit untuk semua modul di atas.
- **README.md** — cara menjalankan (satu perintah, tanpa instalasi tambahan) dan daftar library.

## 9. Kebutuhan Non-Fungsional

- **Kebenaran:** untuk setiap kata di daftar kata (dan sampel acak minimal 10.000 kombinasi huruf), D(E(M)) harus sama dengan M.
- **Kebijakan library:** inti RSA (FPB, invers modulo, eksponensiasi modular, uji prima, pembuatan kunci, encoding) ditulis sendiri. Tidak dipakai di kode inti: pustaka kriptografi atau matematika pihak ketiga (pycryptodome, rsa, cryptography, sympy, gmpy2) dan fungsi bawaan yang menyembunyikan aritmetika modular (math.gcd, pow tiga argumen, pow(e, -1, m)). Boleh dipakai seperlunya: random atau secrets (bilangan acak), tkinter (GUI), unittest (uji). Semua library dicantumkan di makalah.
- **Performa:** pembuatan kunci default di bawah 1 detik; enkripsi atau dekripsi satu blok di bawah 100 ms; pembuatan kunci acak sampai 512 bit per bilangan prima di bawah 10 detik.
- **Kompatibilitas:** Python 3.8 ke atas tanpa pip install. Tkinter sudah ikut di installer Python untuk Windows dan macOS; di Linux mungkin perlu paket python3-tk.
- **Keterbacaan:** docstring dan komentar berbahasa Indonesia yang menjelaskan rumus RSA di setiap fungsi.
- **Reproduksibilitas:** opsi seed acak agar pengujian dan demo bisa diulang.
- **Kesalahan input:** pesan jelas dan program tidak pernah berhenti karena input yang salah.

## 10. Rancangan Tampilan (GUI dan CLI)

**Susunan GUI (target).** Kiri: papan 6 baris × 5 kolom dengan kotak hijau, kuning, dan abu-abu, di bawahnya papan huruf A–Z. Kanan: kunci publik (n, e), sandi misteri C, panel kripto (M dan cipher tebakan), dan tombol Verifikasi sertifikat. Menu atas: Permainan baru, ukuran kunci, Lab Kripto (P2). Tangkapan layar tiap kondisi (awal, di tengah permainan, menang, kalah, verifikasi sertifikat) disiapkan untuk makalah.

Contoh sesi CLI dengan kata rahasia BUNGA dan parameter default (susunan yang sama dipakai di GUI):

```
=== WORDLE KRIPTO ===
Kunci publik (n, e) : (2602632031, 65537)
Sandi misteri (C)   : 587403072

Tebakan 1/6 > bukan
 B  U  K  A  N
 🟩 🟩 ⬛ 🟨 🟨
 [panel kripto] cipher tebakan = 293955741 (berbeda dari C)

Tebakan 2/6 > bunga
 B  U  N  G  A
 🟩 🟩 🟩 🟩 🟩
 [panel kripto] cipher tebakan = 587403072 (sama dengan C)

Menang dalam 2 tebakan! Pembuktian: 587403072^154713473 mod 2602632031 = 0120130600 → BUNGA
```

## 11. Luaran Makalah

Makalah adalah luaran akhir yang dinilai bersama program, dan harus menjelaskan projek, program, tampilannya, serta pemanfaatan aritmetika modular dalam RSA.

**Sampul.** Judul, mata kuliah, dosen, tahun, dan nama seluruh anggota kelompok (tambahkan NIM bila diminta).

**Kerangka isi.**

1. Pendahuluan: latar belakang, tujuan, ruang lingkup, dan ketentuan projek.
2. Landasan teori: aritmetika modular (kongruensi, operasi mod, FPB dan algoritma Euclid, invers modulo, teorema kecil Fermat), kriptografi klasik singkat, RSA, dan uji primalitas.
3. Rancangan dan implementasi program: arsitektur modul, alur permainan, algoritma utama dengan potongan kode, serta daftar library yang dipakai beserta alasannya.
4. Antarmuka dan pengujian: tangkapan layar GUI untuk setiap kondisi dan hasil uji dengan data uji di bagian 6.
5. Kontribusi anggota.
6. Penutup: kesimpulan, keterbatasan (RSA textbook, kunci kecil, serangan kamus), dan saran.
7. Daftar pustaka (buku teks mata kuliah; sesuaikan edisinya).

**Pemetaan aritmetika modular ke program.** Bahan untuk bab 2 dan 3. Penjelasan ini hanya ditulis di makalah dan bukan fitur program.

- Syarat kunci: gcd(e, φ) = 1 diperiksa dengan algoritma Euclid.
- Kunci privat: d ≡ e^−1 (mod φ), dihitung dengan algoritma Euclid yang diperluas (cari\_d).
- Enkripsi dan dekripsi: C ≡ M^e (mod n) dan M ≡ C^d (mod n); kebenarannya bertumpu pada e·d ≡ 1 (mod φ) dan teorema kecil Fermat (turunan lengkap ada di buku teks).
- Eksponensiasi cepat: kuadrat-dan-kali dengan reduksi mod n di setiap langkah.
- Miller–Rabin: memeriksa a^m mod n berdasarkan teorema kecil Fermat.
- Tanda tangan: S ≡ R^d (mod n) dan verifikasi S^e ≡ R (mod n).
- Mode sandi klasik (P2): (p + k) mod 26 dan invers modulo 26 pada sandi affine.

**Tabel pembagian tugas dan kontribusi.** Isi nama sejak hari ini dan perbarui di akhir; tabel yang sama dipindahkan ke makalah.

| Anggota | Peran | Kode | Bagian makalah |
| --- | --- | --- | --- |
| (isi nama) | RSA core dan pengujian | rsa\_core.py, encoding.py, tests | Landasan teori (aritmetika modular) |
| (isi nama) | Mesin Wordle dan Game Master | wordle\_engine.py, game\_master.py | Rancangan dan implementasi program |
| (isi nama) | Antarmuka | gui.py, main.py | Antarmuka dan pengujian |
| (isi nama) | Makalah dan dokumentasi | README.md, kata.txt | Pendahuluan, penutup, penyusunan akhir |

## 12. Kriteria Penerimaan

1. Dengan kunci contoh dosen (n = 2537, e = 13, d = 937), enkripsi STOP menghasilkan 2081 2182 dan dekripsi 0981 0461 menghasilkan HELP.
2. Dengan parameter default, BUNGA terenkripsi menjadi 587403072 dan terdekripsi kembali menjadi BUNGA; ZZZZZ lolos uji bolak-balik.
3. Pembuatan kunci menolak: p = q, p atau q bukan prima, gcd(e, φ) ≠ 1, e di luar rentang 1 < e < φ, dan n < 2525252525 pada mode game. Setiap penolakan memberi pesan yang jelas.
4. Rahasia ABCDE dengan tebakan AAXXX menghasilkan hijau, abu-abu, abu-abu, abu-abu, abu-abu.
5. Tebakan tidak valid (bukan 5 huruf, mengandung angka, tidak ada di daftar kata) tidak mengurangi jumlah percobaan.
6. Kalah setelah tebakan ke-6 yang salah, dan kata asli ditampilkan.
7. Sebelum permainan berakhir, layar tidak pernah menampilkan d maupun kata rahasia.
8. Seluruh uji unit lulus, dan RSA(43, 59, 13) tidak lagi menghasilkan error.
9. FPB, invers modulo, dan eksponensiasi modular buatan sendiri memberi hasil sama dengan fungsi bawaan pada minimal 1000 kasus acak (fungsi bawaan dipakai hanya di berkas uji).
10. Daftar import di kode inti hanya berisi pustaka standar yang tercantum di README dan makalah.
11. Program berjalan dari .zip yang baru diekstrak dengan satu perintah, tanpa instalasi tambahan.
12. (P1) GUI menjalankan seluruh alur P0 dan tidak berhenti saat input salah.
13. (P1) Untuk setiap ukuran kunci acak yang tersedia, p dan q lolos uji Miller–Rabin, n memenuhi syarat blok, dan uji bolak-balik lulus; Miller–Rabin buatan sendiri memberi klasifikasi sama dengan pembagian percobaan untuk semua bilangan di bawah 10000.
14. (P1) Sertifikat hasil asli terverifikasi dan gagal bila satu angka diubah; kunci tanda tangan berbeda dari kunci enkripsi game. Data uji slide: MEET AT NOON menghasilkan 0817 0555 1310 2173 1026 dan terverifikasi.
15. Makalah memuat sampul dengan seluruh nama anggota, penjelasan aritmetika modular, tangkapan layar UI, daftar library, dan tabel kontribusi anggota.

## 13. Jadwal dan Pengumpulan (deadline 29 Oktober 2026)

1. **Minggu, 25 Oktober.** Kode: setujui PRD, bagi tugas, mulai rsa\_core.py (perbaiki cek\_gcd, tulis FPB, Euclid diperluas, kuadrat-dan-kali). Makalah: kerangka dan pembagian bab.
2. **Senin, 26 Oktober.** Kode: rsa\_core, encoding, dan uji unit lulus (kriteria 1 sampai 3, 8, 9); mesin Wordle. Makalah: bab 1 dan draf bab 2.
3. **Selasa, 27 Oktober.** Kode: Game Master dan CLI berjalan dari awal sampai akhir, semua P0 selesai; mulai GUI. Makalah: bab 2 selesai, bab 3 dimulai.
4. **Rabu, 28 Oktober.** Kode: GUI, Miller–Rabin dan ukuran kunci, sertifikat bertanda tangan; **kode dibekukan malam hari**; ambil tangkapan layar. Makalah: bab 3 dan 4.
5. **Kamis, 29 Oktober (deadline).** Susun makalah akhir (sampul, tabel kontribusi, daftar pustaka), uji program dari .zip bersih, lalu satu anggota mengirim lewat Google Form. Kirim lebih awal, jangan menunggu jam terakhir.

**Batas pemotongan.** Fitur P1 atau P2 yang belum lulus uji pada Rabu sore dikeluarkan dari .zip dan makalah, supaya yang dijelaskan adalah yang benar-benar berjalan. Link Google Form belum ada; pantau grup kelas dan kirim begitu link tersedia.

**Daftar periksa pengumpulan.**

- [ ] Folder proyek berisi kode, kata.txt, tests, dan README.md
- [ ] File .zip dibuat dan diuji dari ekstraksi bersih
- [ ] Makalah selesai (format mengikuti petunjuk Google Form)
- [ ] Sampul memuat nama seluruh anggota
- [ ] Tabel kontribusi anggota ada di makalah
- [ ] Satu orang mengirim lewat Google Form sebelum 29 Oktober 2026

**Presentasi.** Bila ada waktu, projek dipresentasikan sebelum UAS; skrip demo disiapkan sebagai F-18.

## 14. Risiko dan Pertanyaan Terbuka

**Risiko**

- Waktu sangat sempit: sisa waktu sampai 29 Oktober hanya beberapa hari. Mitigasi: semua P0 selesai 27 Oktober, kode dibekukan 28 Oktober, dan fitur yang belum lulus uji dipotong.
- Penilaian kompleksitas dan penilaian jumlah library saling tarik: terlalu banyak library menurunkan nilai, terlalu sedikit fitur menurunkan kompleksitas. Mitigasi: algoritma inti ditulis sendiri dan fitur P1 dikerjakan lebih dulu.
- Link Google Form menyusul dan format pengumpulan makalah belum jelas, sehingga ada risiko salah kirim atau terlambat.
- Daftar kata bahasa Indonesia perlu disaring agar hanya berisi kata baku 5 huruf (misalnya dari KBBI) dan tanpa huruf di luar A–Z.
- Pemahaman tim atas cari\_d (Euclid diperluas) dan Miller–Rabin masih perlu dilatih, berisiko saat tanya jawab atau presentasi.
- Kesalahan pengisi nol di kiri saat decoding mudah terjadi dan menghasilkan kata yang salah untuk huruf awal A, B, C.

**Pertanyaan terbuka**

1. Apa format dan panjang makalah (PDF atau Word, jumlah halaman, template), dan apakah makalah diunggah di Google Form bersama .zip?
2. Berapa anggota kelompok dan siapa saja, agar tabel pembagian tugas bisa diisi?
3. Apakah ada ketentuan mengenai penggunaan AI untuk kode dan makalah?
4. Apakah daftar kata harus bahasa Indonesia, bahasa Inggris, atau keduanya?

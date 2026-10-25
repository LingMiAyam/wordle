def cek_prima(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False  #Eliminasi semua angka genap
    
    #Cek hanya angka ganjil sampai akar dari n
    limit = int(n**0.5) + 1
    for i in range(3, limit, 2):
        if n % i == 0:
            return False
            
    return True

def nilai_n(p, q):
        n = p * q
        return n

def cek_gcd(p, q, e):
    dibagi = (p - 1) * (q - 1)
    pembagi = e
    sisa = -1  

    while sisa != 0:
        bil_pembagi = dibagi // pembagi
        sisa = dibagi - (bil_pembagi * pembagi)
        
        if sisa != 0:  
            dibagi = pembagi
            pembagi = sisa

    if pembagi == 1:
        return True
    else:
        return False

def cari_d(e, phi): #invers e buat dekripsi (ini dr ai blm ku pahamin bgt)
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    _, x, _ = extended_gcd(e, phi)
    return (x % phi + phi) % phi

def RSA(p, q, e):
    if p == q:
        print('Nilai p dan q tidak boleh sama')
        return

    if not cek_prima(p):
        print('p bukan bilangan prima, tolong ubah angka p')
        return

    if not cek_prima(q):
        print('q bukan bilangan prima, tolong ubah angka q')
        return

    n = nilai_n(p, q)
    phi = (p - 1) * (q - 1)

    if not cek_gcd(phi, e):
        print('Silahkan menentukan ulang nilai p, q, e (GCD e dan phi harus 1)')
        return

    # Hitung kunci rahasia/privat d (dr ai jg ini)
    d = cari_d(e, phi)

    # tambahan dr ai buat nampilin key
    print(f"Kunci Publik  (n, e): ({n}, {e})")
    print(f"Kunci Privat  (n, d): ({n}, {d})")

    return (n, e), (n, d)

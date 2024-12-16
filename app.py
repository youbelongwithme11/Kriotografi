from flask import Flask, render_template, request, jsonify
import random
from math import gcd

app = Flask(__name__)

# Fungsi Utility

def is_prime(num):
    """
    Memeriksa apakah sebuah bilangan adalah bilangan prima.
    Sebuah bilangan dianggap prima jika lebih besar dari 1 dan tidak memiliki faktor selain 1 dan dirinya sendiri.
    """
    if num <= 1:
        return False
    for i in range(2, int(num ** 0.5) + 1):  # Periksa faktor hingga akar kuadrat bilangan
        if num % i == 0:
            return False
    return True

def find_coprime(phi):
    """
    Mencari bilangan bulat 'e' sehingga 1 < e < phi dan gcd(e, phi) == 1.
    Ini memastikan bahwa 'e' adalah coprime dengan 'phi', yang diperlukan dalam algoritma RSA.
    """
    for e in range(2, phi):
        if gcd(e, phi) == 1:  # Periksa apakah 'e' dan 'phi' adalah coprime
            return e

def generate_rsa_keys(p=None, q=None):
    """
    Menghasilkan kunci RSA berdasarkan dua bilangan prima p dan q.
    Jika p atau q tidak diberikan, bilangan prima akan dipilih secara acak.
    - Menghitung nilai n (hasil perkalian p dan q).
    - Menghitung phi (totient Euler dari n).
    - Menentukan kunci publik (e, n) dan kunci privat (d, n).
    """
    p = int(p) if p else random.choice([11, 13, 17, 19])  # Pilih p jika tidak diberikan
    q = int(q) if q else random.choice([11, 13, 17, 19])  # Pilih q jika tidak diberikan

    if not is_prime(p) or not is_prime(q):  # Pastikan p dan q adalah bilangan prima
        return {"error": "P atau Q harus bilangan prima."}

    n = p * q  # Hitung nilai n
    phi = (p - 1) * (q - 1)  # Hitung nilai totient phi
    e = find_coprime(phi)  # Cari kunci publik e
    d = pow(e, -1, phi)  # Cari kunci privat d menggunakan invers modular

    return {
        "details": {"p": p, "q": q, "phi": phi},
        "public_key": (e, n),
        "private_key": (d, n),
    }

# Rute Flask

@app.route("/")
def index():
    """
    Menampilkan halaman utama dengan template HTML.
    """
    return render_template("index.html")

@app.route("/generate_keys", methods=["POST"])
def generate_keys():
    """
    API untuk menghasilkan kunci RSA berdasarkan input p dan q dari pengguna.
    Jika terjadi kesalahan (p atau q tidak valid), kembalikan pesan error.
    """
    data = request.get_json()
    p = data.get("p")
    q = data.get("q")
    result = generate_rsa_keys(p, q)
    if "error" in result:
        return jsonify({"error": result["error"]}), 400  # Kembalikan kode 400 jika ada error
    return jsonify(result)

@app.route("/encrypt", methods=["POST"])
def encrypt_message():
    """
    API untuk mengenkripsi pesan menggunakan kunci publik (e, n).
    Setiap karakter dalam pesan dikonversi menjadi nilai ASCII dan dienkripsi.
    """
    data = request.get_json()
    message = data.get("message")
    e = int(data.get("e"))
    n = int(data.get("n"))

    encrypted = []
    for char in message:
        ascii_val = ord(char)  # Konversi karakter ke nilai ASCII
        part1 = pow(ascii_val // 10, e, n)  # Bagian pertama ASCII
        part2 = pow(ascii_val % 10, e, n)  # Bagian kedua ASCII
        encrypted.append(f"{part1}.{part2}")  # Gabungkan bagian terenkripsi
    return jsonify({"encrypted": encrypted})

@app.route("/decrypt", methods=["POST"])
def decrypt_message():
    """
    API untuk mendekripsi pesan terenkripsi menggunakan kunci privat (d, n).
    Setiap pasangan bagian terenkripsi diubah kembali menjadi karakter asli.
    """
    data = request.get_json()
    encrypted = data.get("encrypted")
    d = int(data.get("d"))
    n = int(data.get("n"))

    decrypted = []
    for cipher in encrypted:
        part1, part2 = map(int, cipher.split('.'))  # Pisahkan bagian terenkripsi
        plain1 = pow(part1, d, n)  # Dekripsi bagian pertama
        plain2 = pow(part2, d, n)  # Dekripsi bagian kedua
        ascii_val = plain1 * 10 + plain2  # Gabungkan menjadi nilai ASCII asli
        decrypted.append(chr(ascii_val))  # Konversi ASCII menjadi karakter
    return jsonify({"decrypted": ''.join(decrypted)})  # Gabungkan hasil dekripsi

if __name__ == "__main__":
    """
    Menjalankan aplikasi Flask dalam mode debug untuk pengembangan.
    """
    app.run(debug=True)

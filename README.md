# 📈 Tutorial Penggunaan Project Prediksi Time Series (GitHub)

> **Disclaimer**: DYOR (Do Your Own Research) & NFA (Not Financial Advice)

Dokumen ini berisi **tutorial sederhana dan step-by-step** untuk menjalankan project prediksi data time series menggunakan data dari **yfinance**, memprosesnya, melakukan prediksi dengan model, dan menyimpan hasilnya ke dalam file CSV.

---

## 1️⃣ Persiapan Awal

### 1. Pastikan Python Sudah Terinstall

Disarankan menggunakan **Python 3.9+**.

Cek versi Python:

```bash
python --version
```

---

### 2. Install Library dari `requirements.txt`

Sebelum menjalankan kode apa pun, **pastikan semua library sudah terinstall**.

```bash
pip install -r requirements.txt
```

Jika menggunakan virtual environment (disarankan):

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

---

## 2️⃣ Alur Kerja Program (High Level)

Secara umum, alur kerja project ini adalah:

1. Fetch data dari **yfinance**
2. Preprocessing data (normalisasi & hidden state)
3. Load model prediksi
4. Melakukan prediksi
5. Menyimpan hasil prediksi ke dalam **CSV**
6. Menjalankan website untuk menampilkan hasil prediksi

---

## 3️⃣ Step-by-Step Proses Detail

### 🔹 Step 1: Fetch Data dari yfinance

Program akan mengambil data historis Bitcoin menggunakan library **yfinance**.

Data yang diambil biasanya mencakup:

* Open
* High
* Low
* Close
* Volume

Data ini akan digunakan sebagai input utama untuk model.

📌 **Pastikan koneksi internet aktif**, karena data diambil langsung dari Yahoo Finance.

---

### 🔹 Step 2: Preprocessing Data

Setelah data berhasil di-fetch, data akan diproses dengan tahapan berikut:

#### a. Normalisasi Data

* Data dinormalisasi agar berada pada skala tertentu
* Bertujuan untuk meningkatkan performa dan stabilitas model

#### b. Hidden State Preparation

* Data diubah ke dalam bentuk **sequence / window**
* Digunakan untuk model berbasis time-series (misalnya LSTM)

📌 **LOOKBACK WAJIB 30 (JANGAN DIGANTI)**

```python
LOOKBACK = 30
```

Nilai ini digunakan untuk membentuk urutan data historis yang dipakai oleh model.

---

### 🔹 Step 3: Load Model

Model prediksi yang sudah dilatih sebelumnya akan di-load dari file.

Contoh:

* Model LSTM
* Model berbasis neural network lainnya

Model ini akan menerima data hasil preprocessing sebagai input.

---

### 🔹 Step 4: Melakukan Prediksi

Setelah model berhasil di-load:

* Data input dimasukkan ke model
* Model menghasilkan nilai prediksi untuk periode ke depan

Prediksi ini bersifat **estimasi matematis**, bukan kepastian.

---

### 🔹 Step 5: Menyimpan Hasil ke CSV

Hasil prediksi akan disimpan dalam bentuk file **CSV** agar:

* Mudah dianalisis
* Bisa digunakan ulang
* Bisa ditampilkan di website

Contoh output:

```
prediction_result.csv
```

File ini biasanya berisi:

* Tanggal prediksi
* Nilai hasil prediksi

---

## 4️⃣ Mengatur Panjang Prediksi

Jika ingin **mengubah panjang periode prediksi**, silakan ubah bagian berikut:

```python
start_date = end_date - timedelta(days=60)
```

### ⚠️ Aturan Penting

* **LOOKBACK = 30 → JANGAN DIUBAH**
* **Minimal `timedelta` = 30 hari**

❌ Contoh yang SALAH:

```python
start_date = end_date - timedelta(days=10)
```

✅ Contoh yang BENAR:

```python
start_date = end_date - timedelta(days=45)
```

---

## 5️⃣ Menjalankan Website

Setelah proses prediksi selesai dan file **CSV berhasil dibuat**, kamu dapat menampilkan hasil prediksi melalui website statis menggunakan **Python built-in HTTP server**.

### Langkah-langkah:

1. Pastikan file CSV hasil prediksi berada di folder yang akan ditampilkan (misalnya folder `web/` atau root project).

2. Masuk ke direktori project atau direktori website:

```bash
cd path/ke/folder_project
```

3. Jalankan Python HTTP Server di port **8000**:

```bash
python -m http.server 8000
```

4. Buka browser dan akses:

```
http://localhost:8000
```

5. Website akan memuat data dari file CSV dan menampilkan hasil prediksi dalam bentuk grafik.

📌 Server ini bersifat **lokal dan sederhana**, cocok untuk testing dan preview hasil prediksi.

---

## 6️⃣ Ringkasan Singkat

✔ Install dependency dari `requirements.txt`
✔ Jalankan kode fetch untuk mengambil data dari yfinance
✔ Data diproses (normalisasi & hidden state)
✔ Model di-load dan melakukan prediksi
✔ Hasil prediksi disimpan ke CSV
✔ Website dijalankan untuk menampilkan hasil

---

## ⚠️ Disclaimer Akhir

**DYOR (Do Your Own Research)**
**NFA (Not Financial Advice)**

Project ini dibuat untuk **tujuan edukasi dan eksplorasi teknis**, bukan sebagai saran investasi atau keputusan finansial.

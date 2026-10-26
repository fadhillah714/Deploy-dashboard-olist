# Proyek Analisis Data E-Commerce Olist

## Deskripsi
Proyek ini menganalisis dataset Brazilian E-Commerce Public Dataset by Olist. Notebook mencakup proses pengumpulan dan penilaian data, pembersihan data, eksplorasi tren pesanan dan pembayaran, analisis durasi pengiriman terhadap skor ulasan, serta segmentasi pelanggan menggunakan RFM.

Dashboard Streamlit menyediakan filter periode, status pesanan, dan skor ulasan, serta visualisasi tren pesanan, pembayaran, durasi pengiriman, dan distribusi skor ulasan.

## Struktur folder
```text
Submission_Proyek_Analisis_Data_Final/
├── Proyek_Analisis_Data.ipynb
├── dashboard.py
├── requirements.txt
├── README.md
├── url.txt
├── .streamlit/
│   └── config.toml        # tema warna dashboard (burgundy/krem)
└── data/
    ├── main_data.csv
    ├── customers_dataset.csv
    ├── geolocation_dataset.csv
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── order_payments_dataset.csv
    ├── order_reviews_dataset.csv
    ├── products_dataset.csv
    ├── product_category_name_translation.csv
    └── sellers_dataset.csv
```

## Persiapan lingkungan
Disarankan menggunakan Python 3.10 atau versi yang kompatibel dengan versi dependensi di `requirements.txt`.

Buka terminal di folder proyek, lalu jalankan:

```bash
python -m venv .venv
```

Aktifkan environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Pasang dependensi:

```bash
python -m pip install -r requirements.txt
```

## Menjalankan dashboard
Pastikan `data/main_data.csv` tersedia, kemudian jalankan:

```bash
streamlit run dashboard.py
```

Streamlit akan menampilkan alamat lokal pada terminal, umumnya `http://localhost:8501`. Alamat lokal hanya dapat diakses dari lingkungan yang sesuai dan bukan URL deployment publik.

## Ringkasan dashboard
- Jumlah pesanan unik berdasarkan filter.
- Total pembayaran (BRL).
- Rata-rata skor ulasan.
- Median durasi pengiriman untuk data tanggal pengiriman valid.
- Tren pesanan dan pembayaran per bulan.
- Median durasi pengiriman berdasarkan skor ulasan.
- Distribusi skor ulasan dan tabel data hasil filter.

## Catatan interpretasi
- Dashboard menggunakan `main_data.csv` yang diekspor dari notebook.
- Durasi pengiriman dihitung dari tanggal pembelian sampai tanggal diterima pelanggan; baris tanpa tanggal valid atau dengan durasi negatif tidak masuk ringkasan durasi.
- Hubungan durasi pengiriman dan skor ulasan bersifat deskriptif dan tidak dengan sendirinya membuktikan sebab-akibat.
- Nilai pembayaran berasal dari dataset dan ditampilkan dalam BRL.
- Pastikan seluruh sel notebook dapat dijalankan ulang dari kernel baru sebelum pengumpulan.

## Deployment
Setelah dashboard berhasil diuji secara lokal, deploy sesuai platform yang diperbolehkan oleh instruksi kelas. Masukkan URL publik yang benar-benar aktif ke `url.txt`. Jangan menggunakan alamat `localhost` sebagai URL publik.

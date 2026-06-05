# Deteksi AI Terbaru

Website AI Detection modern untuk penelitian skripsi dengan tema "Penerapan Fuzzy Logic Sugeno dalam Mendeteksi Gambar AI".

## Struktur proyek

- `app.py` - Flask backend sederhana untuk upload dan response deteksi.
- `templates/index.html` - Halaman utama UI dashboard.
- `static/css/styles.css` - Styling dark mode, glassmorphism, neon cyberpunk.
- `static/js/script.js` - Interaktivitas upload, charts, dan background particle.
- `requirements.txt` - Dependensi Python.

## Jalankan proyek

1. Buat virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependensi:

```powershell
python -m pip install -r requirements.txt
```

3. Jalankan server:

```powershell
python app.py
```

4. Buka browser ke `http://127.0.0.1:5000`

## Catatan

- Bagian deteksi saat ini menggunakan response dummy untuk UI.
- Anda dapat menghubungkan backend ke OpenCV, MATLAB, dan model Fuzzy Sugeno sesuai kebutuhan penelitian.

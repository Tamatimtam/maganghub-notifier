# MagangHub 24/7 Vacancy Watcher & Offline Backup

Script otomatis yang berjalan 24/7 di **GitHub Actions** untuk memantau pembukaan lowongan MagangHub Kemnaker RI.

### Fitur:
1. **Always-On di Cloud**: Berjalan gratis di GitHub Actions setiap 5 menit tanpa laptop harus nyala.
2. **Push Notification ke HP**: Menggunakan **[ntfy.sh](https://ntfy.sh)** dengan level *urgent/alarm*.
3. **Offline Backup**: Begitu lowongan muncul, data langsung di-scrape dan di-backup ke `lowongan_maganghub.html` sehingga bisa dibaca offline meskipun server Kemnaker sedang down.

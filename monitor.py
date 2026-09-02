#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import re
import time
import os
import sys

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "tama-maganghub-alert")
BASE_URL = "https://maganghub.kemnaker.go.id"
LOWONGAN_URL = f"{BASE_URL}/magang-nasional/lowongan"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def send_ntfy(title, message, priority="urgent", tags="rotating_light,bell"):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    req = urllib.request.Request(
        url,
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": tags,
            "Click": LOWONGAN_URL,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[{time.strftime('%H:%M:%S')}] Notifikasi ntfy terkirim ke topik: {NTFY_TOPIC}")
    except Exception as e:
        print(f"Gagal kirim ntfy: {e}")

def fetch_page(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def extract_vacancies(html):
    total = 0
    m_text = re.search(r'Ditemukan <strong>(\d+)</strong> lowongan', html)
    if m_text:
        total = int(m_text.group(1))
    else:
        m_json = re.search(r'\"total\\\\?\":\s*(\d+)', html)
        if m_json:
            total = int(m_json.group(1))

    vacancies = []
    item_matches = re.finditer(r'\{\\"id\\":\\"([0-9a-f\-]+)\\",\\"positionName\\":\\"(.*?)\\"', html)
    for m in item_matches:
        vac_id = m.group(1)
        vac_name = m.group(2).encode('utf-8').decode('unicode_escape', errors='ignore')
        vacancies.append({"id": vac_id, "positionName": vac_name})

    return total, vacancies

def generate_html(vacancies, total, last_updated):
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Katalog Lowongan MagangHub Kemnaker (Offline Backup)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        header {{ border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        h1 {{ margin: 0; color: #38bdf8; font-size: 22px; }}
        .badge {{ background: #0284c7; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: bold; }}
        .search-box {{ width: 100%; box-sizing: border-box; padding: 12px 16px; font-size: 15px; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #fff; margin-bottom: 16px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 16px; color: #fff; }}
        .btn {{ display: block; text-align: center; background: #2563eb; color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold; margin-top: 12px; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>MagangHub Offline Cache</h1>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Update: <strong>{last_updated}</strong> &bull; Total: <span id="count">{total}</span> lowongan</div>
            </div>
            <div class="badge">Live Cache</div>
        </header>
        <input type="text" id="search" class="search-box" placeholder="Cari posisi...">
        <div class="grid" id="list">
"""
    for item in vacancies:
        v_id = item.get("id", "")
        v_name = item.get("positionName", "Lowongan")
        link = f"https://maganghub.kemnaker.go.id/magang-nasional/lowongan/{v_id}"
        html += f"""
            <div class="card" data-title="{v_name.lower()}">
                <h3>{v_name}</h3>
                <a href="{link}" target="_blank" class="btn">Buka di MagangHub &rarr;</a>
            </div>
        """

    html += """
        </div>
    </div>
    <script>
        const s = document.getElementById('search');
        const cards = document.querySelectorAll('.card');
        const c = document.getElementById('count');
        s.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase().trim();
            let v = 0;
            cards.forEach(card => {
                const match = card.dataset.title.includes(q);
                card.style.display = match ? 'flex' : 'none';
                if (match) v++;
            });
            c.innerText = v;
        });
    </script>
</body>
</html>
"""
    with open("lowongan_maganghub.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    is_test = "--test" in sys.argv
    print(f"[{time.strftime('%H:%M:%S')}] Memeriksa MagangHub Kemnaker...")
    
    if is_test:
        print("Mode test: Mengirim notifikasi percobaan ke HP...")
        send_ntfy(
            title="GitHub Actions Connected!",
            message="Script pemantau MagangHub di GitHub Actions berhasil berjalan dan siap memantau 24/7!",
            priority="default",
            tags="white_check_mark,zap"
        )
        return

    try:
        html = fetch_page(LOWONGAN_URL)
        total, vacancies = extract_vacancies(html)
        print(f"[{time.strftime('%H:%M:%S')}] Status: Ditemukan {total} lowongan aktif.")

        prev_total = 0
        if os.path.exists("state.json"):
            try:
                with open("state.json") as f:
                    prev_total = json.load(f).get("total", 0)
            except Exception:
                pass

        with open("state.json", "w") as f:
            json.dump({"total": total, "updatedAt": time.strftime("%Y-%m-%d %H:%M:%S")}, f)

        if total > 0 and total != prev_total:
            print(f"🚨 PORTAL MAGANGHUB RESMI DIBUKA! DITEMUKAN {total} LOWONGAN!")
            send_ntfy(
                title=f"🚨 LOWONGAN MAGANGHUB BUKA! ({total} Posisi)",
                message=f"Buruan buka MagangHub sekarang! Ditemukan {total} lowongan magang yang baru saja dipublikasikan.",
                priority="urgent",
                tags="rotating_light,fire"
            )
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            generate_html(vacancies, total, now)
            with open("lowongan_maganghub.json", "w", encoding="utf-8") as f:
                json.dump({"total": total, "vacancies": vacancies, "updatedAt": now}, f, indent=2)

    except Exception as e:
        print(f"Error checking MagangHub: {e}")

if __name__ == "__main__":
    main()

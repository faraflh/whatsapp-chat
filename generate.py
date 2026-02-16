import re
import os
import html
import math
from datetime import datetime

# --- KONFIGURASI ---
NAMA_FILE_CHAT = "_chat.txt"
PESAN_PER_HALAMAN = 2000  # Chat akan dipotong tiap 2000 pesan agar ringan
SENDER_RIGHT = 'raeca'    # Ganti sesuai nama sender kanan
SENDER_LEFT = 'farah'     # Ganti sesuai nama sender kiri

# --- TEMPLATE HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat History - Hal {page_num}</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            background-color: #0b141a;
            color: #e9edef;
            margin: 0;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }}
        .app-container {{
            width: 100%;
            max-width: 800px;
            background-color: #0b141a;
            border-left: 1px solid #202c33;
            border-right: 1px solid #202c33;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        .header {{
            padding: 10px 16px;
            background-color: #202c33;
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .back-icon {{
            color: #aebac1;
            font-size: 20px;
            text-decoration: none;
            margin-right: 5px;
        }}
        .profile-pic {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            background-color: #6a7175;
        }}
        .user-info {{
            display: flex;
            flex-direction: column;
        }}
        .user-info h2 {{
            margin: 0;
            font-size: 16px;
            font-weight: 500;
            color: #e9edef;
        }}
        .user-info span {{
            font-size: 12px;
            color: #8696a0;
        }}

        .header-right {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        .nav-icon {{
            fill: #aebac1;
            width: 24px;
            height: 24px;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        .nav-icon.disabled {{
            opacity: 0.2;
            cursor: default;
        }}
        .header h2 {{ margin: 0; font-size: 16px; color: #e9edef; }}

        .pagination {{ display: flex; gap: 10px; }}
        .btn {{
            text-decoration: none;
            color: #00a884;
            background: #111b21;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
            border: 1px solid #202c33;
        }}
        .btn:hover {{ background: #202c33; }}
        .btn.disabled {{ opacity: 0.3; pointer-events: none; }}

        .chat-area {{
            flex: 1;
            padding: 20px 15px;
            background-image: url('https://wallpapercave.com/wp/wp7130410.jpg');
            background-repeat: repeat;
            background-blend-mode: overlay;
            background-attachment: fixed;
            padding-bottom: 80px; /* Space for bottom nav */
        }}

        .msg-row {{ display: flex; width: 100%; margin-bottom: 2px; }}
        .msg-bubble {{
            max-width: 80%;
            padding: 6px 10px 8px 10px;
            border-radius: 10px;
            position: relative;
            font-size: 14px;
            line-height: 1.5;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
            word-wrap: break-word;
        }}

        /* Kiri */
        .msg-left {{ justify-content: flex-start; }}
        .msg-left .msg-bubble {{ background-color: #202c33; border-top-left-radius: 0; }}
        .sender-name {{ font-size: 12.5px; font-weight: 500; color: #f67280; display: block; margin-bottom: 3px; }}

        /* Kanan */
        .msg-right {{ justify-content: flex-end; }}
        .msg-right .msg-bubble {{ background-color: #005c4b; border-top-right-radius: 0; }}

        /* Media */
        img, video {{ max-width: 100%; border-radius: 8px; display: block; margin-bottom: 4px; }}

        /* Sticker */
        .sticker-row .msg-bubble {{ background: transparent !important; box-shadow: none !important; padding: 0; }}
        .sticker-img {{ width: 130px; }}

        .meta {{
            float: right; margin-left: 8px; margin-top: 6px;
            font-size: 10.5px; color: #8696a0;
        }}
        .msg-right .meta {{ color: #83c6b9; }}

        .date-divider {{
            align-self: center; background-color: #1f2c34; color: #8696a0;
            padding: 5px 12px; border-radius: 8px; font-size: 12px;
            margin: 20px auto; border: 1px solid #28343e; text-align: center; width: fit-content;
        }}

        /* Bottom Nav */
        .bottom-nav {{
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: #202c33; padding: 10px 20px; border-radius: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); display: flex; gap: 15px; border: 1px solid #2f3b43;
        }}
    </style>
</head>
<body>

<div class="app-container">

    <div class="header">
        <div class="header-left">
            <span class="back-icon">❮</span>
            <img src="ava.jpg" class="profile-pic" alt="pfp">
            <div class="user-info">
                <h2>faw❤️</h2>
                <span>Hal {page_num} dari {total_pages}</span>
            </div>
        </div>
        
        <div class="header-right">
            <div class="pagination">
            <a href="{prev_link}" class="btn {prev_disabled}">❮ Prev</a>
            <a href="{next_link}" class="btn {next_disabled}">Next ❯</a>
        </div>
        </div>
    </div>

    <div class="chat-area">
        {chat_content}
    </div>

    <!-- <div class="bottom-nav">
        <a href="{prev_link}" class="btn {prev_disabled}">❮ Sebelumnya</a>
        <span style="color:#aaa; align-self:center; font-size:12px;">{page_num} / {total_pages}</span>
        <a href="{next_link}" class="btn {next_disabled}">Selanjutnya ❯</a>
    </div> -->
</div>

</body>
</html>
"""

def format_time_short(time_str):
    """
    Mengubah format '10.33.22 PM' menjadi '22.33' (24 Jam)
    atau setidaknya membuang detik.
    """
    try:
        # Bersihkan karakter invisible space yang sering ada di Android (\u202f)
        clean_str = time_str.replace('\u202f', ' ').strip()

        # Coba parsing format 12 jam dengan detik (10.33.22 PM)
        # Note: WA format sering pakai titik sbg pemisah waktu
        clean_str = clean_str.replace('.', ':')

        dt = datetime.strptime(clean_str, "%I:%M:%S %p")
        return dt.strftime("%H.%M")
    except ValueError:
        try:
            # Coba parsing tanpa detik jika ada kasus lain
            dt = datetime.strptime(clean_str, "%I:%M %p")
            return dt.strftime("%H.%M")
        except ValueError:
            # Fallback manual: Ambil 5 karakter pertama saja (10.33)
            # Ini jika formatnya benar-benar aneh/berbeda
            # This part handles cases where even datetime parsing fails, ensuring robustness.
            parts = clean_str.split(':')
            if len(parts) >= 2:
                return parts[0] + '.' + parts[1]
            else:
                # If it still can't be split reliably, return the original clean_str
                return clean_str

def parse_chat(filepath):
    parsed_data = []
    line_pattern = re.compile(r'^\u005b(\d{2}/\d{2}/\d{2}),\s+(\d{1,2}\.\d{2}\.\d{2}[\s\u202f]?[AP]M)\u005d\s+(.*?):\s+(.*)$')
    attach_pattern = re.compile(r'[\u200e]?<?attached:\s*(.*?)>')

    if not os.path.exists(filepath):
        print("File tidak ditemukan.")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        current_msg = None
        for line in f:
            clean_line = re.sub(r'[\u200e\u200f]', '', line).strip()
            match = line_pattern.match(clean_line)
            if match:
                if current_msg: parsed_data.append(current_msg)
                date, time_raw, sender, content = match.groups()
                # UBAH FORMAT WAKTU DI SINI
                short_time = format_time_short(time_raw)

                current_msg = {
                    'date': date, 'time': short_time, 'sender': sender.strip(),
                    'content': content, 'media': None, 'type': 'text'
                }
            else:
                if current_msg: current_msg['content'] += "\\n" + clean_line
        if current_msg: parsed_data.append(current_msg)

    # Media Check
    for msg in parsed_data:
        media_match = attach_pattern.search(msg['content'])
        if media_match:
            filename = media_match.group(1)
            msg['media'] = filename
            msg['content'] = attach_pattern.sub('', msg['content']).strip()
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.webp': msg['type'] = 'sticker'
            elif ext in ['.jpg', '.jpeg', '.png']: msg['type'] = 'image'
            elif ext == '.mp4': msg['type'] = 'video'

    return parsed_data

def generate_html_page(data, page_num, total_pages):
    html_output = ""
    last_date = ""

    for msg in data:
        if msg['date'] != last_date:
            html_output += f'<div class="date-divider">{msg["date"]}</div>'
            last_date = msg['date']

        # Posisi
        sender_lower = msg['sender'].lower()
        pos_class = 'msg-right' if SENDER_RIGHT in sender_lower else 'msg-left'

        # Sticker
        is_sticker = (msg['type'] == 'sticker')
        row_class = "sticker-row" if is_sticker else ""

        # Media
        media_html = ""
        if msg['type'] == 'sticker':
            media_html = f'<img src="{msg["media"]}" class="sticker-img" loading="lazy">'
        elif msg['type'] == 'image':
            media_html = f'<img src="{msg["media"]}" loading="lazy">'
        elif msg['type'] == 'video':
            # Gunakan preload none agar tidak berat
            media_html = f'<video controls preload="none" poster=""><source src="{msg["media"]}" type="video/mp4"></video>'

        text_content = html.escape(msg['content']).replace('\n', '<br>')
        if not text_content and not media_html: continue

        sender_label = ""
        if pos_class == 'msg-left' and not is_sticker:
            sender_label = f'<span class="sender-name">{msg["sender"]}</span>'

        html_output += f"""
        <div class="msg-row {pos_class} {row_class}">
            <div class="msg-bubble">
                {sender_label}
                {media_html}
                {text_content}
                <div class="meta">{msg['time']}</div>
            </div>
        </div>
        """

    # Generate Link Navigasi
    prev_link = f"chat_page_{page_num-1}.html" if page_num > 1 else "#"
    next_link = f"chat_page_{page_num+1}.html" if page_num < total_pages else "#"
    prev_disabled = "disabled" if page_num == 1 else ""
    next_disabled = "disabled" if page_num == total_pages else ""

    return HTML_TEMPLATE.format(
        page_num=page_num, total_pages=total_pages,
        chat_content=html_output,
        prev_link=prev_link, next_link=next_link,
        prev_disabled=prev_disabled, next_disabled=next_disabled
    )

# --- EXECUTION ---
print("Membaca chat...")
all_messages = parse_chat(NAMA_FILE_CHAT)
total_msgs = len(all_messages)
print(f"Total pesan: {total_msgs}")

total_pages = math.ceil(total_msgs / PESAN_PER_HALAMAN)
print(f"Membuat {total_pages} halaman HTML...")

for i in range(total_pages):
    start_idx = i * PESAN_PER_HALAMAN
    end_idx = start_idx + PESAN_PER_HALAMAN
    chunk = all_messages[start_idx:end_idx]

    page_num = i + 1
    page_content = generate_html_page(chunk, page_num, total_pages)

    filename = f"chat_page_{page_num}.html"
    # Buat halaman pertama juga bisa diakses dengan index.html agar mudah
    if page_num == 1:
        with open("index.html", 'w', encoding='utf-8') as f: f.write(page_content)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(page_content)

    print(f"Halaman {page_num} selesai.")

print("Selesai! Buka 'index.html' untuk mulai membaca.")

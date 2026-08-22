import os
import sys
import json
import urllib.request
import urllib.parse

def send_req(url, data):
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded)
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode())
    except Exception as e:
        print(f"⚠️ Telegram API Error: {e}")
        return None

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "start"
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ Telegram token or chat_id missing. Skipping notification.")
        return

    os.makedirs("output_meta", exist_ok=True)
    msg_file = "output_meta/telegram_msg.id"

    if action == "start":
        manifest = os.environ.get("MANIFEST", "")
        manifest_xml = manifest if manifest.endswith(".xml") else f"{manifest}.xml"
        text = (
            f"⚡ *Lotus-Kernel Build Engine Initialized*\n\n"
            f"📱 *Device:* Redmi Note 10 5G/POCO M3 Pro 5G\n"
            f"🌿 *Branch:* `{manifest_xml}`\n"
            f"🎯 *Target:* {os.environ.get('TARGET', '')}\n"
            f"🔑 *KSU Engine:* {os.environ.get('KSU', '')}\n"
            f"🛠️ *Toolchain:* {os.environ.get('TOOLCHAIN', '')}\n"
            f"🔢 *Build Run:* #{os.environ.get('RUN_NUM', '')}\n\n"
            f"🔄 *Progress:* `[1/4] Preparing build dependencies...`"
        )
        res = send_req(f"https://api.telegram.org/bot{token}/sendMessage", {
            "chat_id": chat_id, "text": text, "parse_mode": "Markdown"
        })
        if res and res.get("result", {}).get("message_id"):
            with open(msg_file, "w") as f:
                f.write(str(res["result"]["message_id"]))
            print(f"✅ Saved Message ID: {res['result']['message_id']}")

    elif action == "progress":
        if not os.path.exists(msg_file):
            return
        with open(msg_file, "r") as f:
            msg_id = f.read().strip()
        manifest = os.environ.get("MANIFEST_NAME", "")
        manifest_xml = manifest if manifest.endswith(".xml") else f"{manifest}.xml"
        text = (
            f"⚡ *Lotus-Kernel Build Engine*\n\n"
            f"📱 *Device:* Redmi Note 10 5G/POCO M3 Pro 5G\n"
            f"🌿 *Branch:* `{manifest_xml}`\n"
            f"🔑 *KSU Engine:* {os.environ.get('KSU_FORK', '')}\n\n"
            f"⚙️ *Progress:* `[2/4] Compiling Kernel source with Clang...` ⏳"
        )
        send_req(f"https://api.telegram.org/bot{token}/editMessageText", {
            "chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "Markdown"
        })

    elif action == "failure":
        manifest = os.environ.get("MANIFEST", "")
        ksu = os.environ.get("KSU", "")
        text = f"❌ *Build Kernel Failed!*\n📱 *Device:* {manifest}\n⚙️ *Fork:* {ksu}"
        send_req(f"https://api.telegram.org/bot{token}/sendMessage", {
            "chat_id": chat_id, "text": text, "parse_mode": "Markdown"
        })

if __name__ == "__main__":
    main()
  

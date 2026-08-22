import os
import sys
import json
import subprocess

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    ksu = os.environ.get("KSU", "KernelSU")
    
    if not token or not chat_id:
        print("⚠️ TELEGRAM_TOKEN atau TELEGRAM_CHAT_ID tidak ditemukan. Skip Telegram notification.")
        return

    # 1. Daftar Fitur
    features = [
        f"KernelSU Engine: {ksu}",
        f"SUSFS Anti-Detection: {os.environ.get('SUSFS', 'false')}",
        f"DroidSpace & OverlayFS: {os.environ.get('DROIDSPACE', 'false')}",
        f"Baseband-Guard: {os.environ.get('BBG', 'false')}",
        f"ThinLTO & -O3: {os.environ.get('LTO', 'false')}",
        f"WireGuard: {os.environ.get('WG', 'false')}",
        f"F2FS Backport: {os.environ.get('F2FS', 'false')}",
        f"ZRAM ZSTD: {os.environ.get('ZSTD', 'false')}",
        f"TCP BBR: {os.environ.get('BBR', 'false')}",
        f"TTL Spoofing: {os.environ.get('TTL', 'false')}"
    ]
    feature_str = "\n".join([f"• {f}" for f in features])

    # 2. Baca Changelog
    changelog_str = ""
    for root, _, files in os.walk("release_assets"):
        for f in files:
            if f == "changelog.txt" and not changelog_str:
                with open(os.path.join(root, f), "r") as cl:
                    changelog_str = cl.read().strip()
                if len(changelog_str) > 300:
                    changelog_str = changelog_str[:300] + "\n... (truncated)"

    # 3. Baca Commit Link
    commit_link = os.environ.get("COMMIT_LINK", "").strip()
    if not commit_link:
        server = os.environ.get("GH_SERVER", "https://github.com")
        repo = os.environ.get("GH_REPO", "")
        sha = os.environ.get("GH_SHA", "")
        if repo and sha:
            commit_link = f"{server}/{repo}/commit/{sha}"
    
    link_str = f"\n🔗 Full Commit History: {commit_link}" if commit_link else ""

    # 4. Fungsi Kirim Dokumen via Curl
    def send_doc(file_path, caption_text):
        file_size = os.path.getsize(file_path)
        if file_size > 52428800:
            print(f"❌ ERROR: File {file_path} > 50MB ({file_size/1024/1024:.2f} MB). Diatas batas Telegram API!")
            sys.exit(1)
            
        cmd = [
            "curl", "-s",
            "-F", f"chat_id={chat_id}",
            "-F", f"document=@{file_path}",
            "-F", f"caption={caption_text}",
            f"https://api.telegram.org/bot{token}/sendDocument"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        try:
            resp = json.loads(res.stdout)
            if resp.get("ok"):
                print(f"✅ Telegram Sent: {os.path.basename(file_path)}")
            else:
                print(f"❌ Telegram Rejected [{os.path.basename(file_path)}]: {resp.get('description')}")
                sys.exit(1)
        except Exception:
            print(f"❌ Response Error: {res.stdout}")
            sys.exit(1)

    # 5. Cari & Kirim File (.zip dan .apk) DENGAN FILTER ARM64/UNIVERSAL
    zips, apks = [], []
    for root, _, files in os.walk("release_assets"):
        for f in files:
            if f.endswith(".zip"):
                zips.append(os.path.join(root, f))
            elif f.endswith(".apk"):
                fname_lower = f.lower()
                # ABAIKAN arsitektur 32-bit dan x86
                if any(arch in fname_lower for arch in ["v7a", "x86", "armeabi"]):
                    continue
                # HANYA AMBIL jika terdapat label arm64 atau universal
                if any(arch in fname_lower for arch in ["arm64", "universal"]):
                    apks.append(os.path.join(root, f))

    print(f"📦 Found ZIPs: {zips}")
    print(f"📱 Found APKs: {apks}")

    for zip_file in zips:
        name = os.path.basename(zip_file)
        size = subprocess.check_output(["du", "-h", zip_file]).decode().split()[0]
        
        sha_hash = "N/A"
        for root, _, files in os.walk("release_assets"):
            if f"{name}.sha256" in files:
                with open(os.path.join(root, f"{name}.sha256"), "r") as f:
                    sha_hash = f.read().strip().split()[0]
                break
                
        caption = (
            f"⚡ Lotus-V1-{ksu} Kernel Ready!\n\n"
            f"📱 Device: Redmi Note 10 5G / Poco M3 Pro 5G (camellia/camellian)\n"
            f"⚙️ KSU Engine: {ksu}\n\n"
            f"🛠️ Active Features:\n{feature_str}\n\n"
            f"📋 Recent Commits:\n{changelog_str}{link_str}\n\n"
            f"📦 File: {name}\n"
            f"📊 Size: {size}\n"
            f"🔑 SHA256: <code>{sha_hash}</code>"
        )
        send_doc(zip_file, caption)

    for apk_file in apks:
        name = os.path.basename(apk_file)
        size = subprocess.check_output(["du", "-h", apk_file]).decode().split()[0]
        
        caption = (
            f"📱 KSU Manager App!\n\n"
            f"⚙️ KSU Engine: {ksu}\n"
            f"📦 File: <code>{name}</code>\n"
            f"📊 Size: {size}"
        )
        send_doc(apk_file, caption)

if __name__ == "__main__":
    main()

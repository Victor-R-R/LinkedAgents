#!/usr/bin/env python3
"""
Publish a LinkedIn image post.
Run: python3 publish_image_post.py
"""
import os, json, subprocess, sys, unicodedata
from pathlib import Path

TOKEN     = os.environ["LINKEDIN_TOKEN"]
PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]

def _find_screenshot() -> Path:
    desktop = Path("/Users/victorrubia/Desktop")
    for f in desktop.iterdir():
        name = unicodedata.normalize("NFC", f.name)
        if "10.15.50" in name and f.suffix.lower() == ".png":
            return f
    raise FileNotFoundError("Screenshot introuvable sur le Desktop.")

IMAGE_PATH = _find_screenshot()

POST_TEXT = """🛠️ Ce matin je suis tombé sur un thème VSCode qui m'a donné l'impression que mon IDE venait d'être upgradé.

Islands Dark. 8 000 stars sur GitHub, et je comprends maintenant pourquoi.

Ce qui m'a surpris c'est que ce n'est pas juste un color scheme. Il injecte du CSS directement dans VSCode pour recréer des panneaux flottants, des bordures verre, des animations sur tout. Tu te retrouves avec quelque chose qui ressemble visuellement à un IDE JetBrains.

Installé en 30 secondes sur mon projet en cours. Je pense pas revenir en arrière.

👇 github.com/bwya77/vscode-dark-islands

#VSCode #OpenSource"""


def run_curl(cmd: list) -> tuple:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout, r.returncode


def initialize_image_upload() -> dict:
    payload = json.dumps({
        "initializeUploadRequest": {
            "owner": f"urn:li:person:{PERSON_ID}"
        }
    })
    stdout, _ = run_curl([
        "curl", "-s",
        "-X", "POST",
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", "LinkedIn-Version: 202503",
        "-H", "X-Restli-Protocol-Version: 2.0.0",
        "-d", payload,
    ])
    try:
        return json.loads(stdout)
    except Exception as e:
        print(f"JSON parse error: {e}\nRaw: {stdout[:500]}")
        return {}


def upload_image(upload_url: str, path: Path) -> str:
    clean_url = upload_url.strip()
    result = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "PUT", clean_url,
        "-H", "Content-Type: image/png",
        "--data-binary", f"@{path}",
    ], capture_output=True, text=True)
    return result.stdout.strip()


def create_post(image_urn: str) -> tuple:
    payload = json.dumps({
        "author": f"urn:li:person:{PERSON_ID}",
        "commentary": POST_TEXT,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": "Islands Dark VSCode Theme",
                "id": image_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    })
    stdout, _ = run_curl([
        "curl", "-s", "-i",
        "-X", "POST", "https://api.linkedin.com/rest/posts",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", "LinkedIn-Version: 202503",
        "-H", "X-Restli-Protocol-Version: 2.0.0",
        "-d", payload,
    ])
    headers_raw, _, body = stdout.partition("\r\n\r\n")
    first_line = headers_raw.split("\r\n")[0] if headers_raw else ""
    status = first_line.split(" ")[1] if " " in first_line else "?"
    post_urn = next(
        (h.split(":", 1)[1].strip() for h in headers_raw.split("\n")
         if h.lower().startswith("x-restli-id:")),
        None,
    )
    return status, post_urn, body


def main():
    print(f"Image : {IMAGE_PATH.name}")
    print(f"Taille: {IMAGE_PATH.stat().st_size / 1_000:.0f} KB\n")

    print("→ 1/3  Initialisation de l'upload image...")
    data = initialize_image_upload()
    val = data.get("value", {})
    if not val or "image" not in val:
        print(f"❌ Échec initializeUpload : {json.dumps(data, indent=2)}")
        sys.exit(1)

    image_urn  = val["image"]
    upload_url = val.get("uploadUrl", "")
    print(f"✓  Image URN  : {image_urn}")

    print("→ 2/3  Upload de l'image...")
    code = upload_image(upload_url, IMAGE_PATH)
    print(f"   HTTP {code}")
    if code not in ("200", "201", "204"):
        print(f"❌ Upload échoué — HTTP {code}")
        sys.exit(1)

    print("   Attente 10s — LinkedIn doit processer l'image...")
    import time; time.sleep(10)

    print("→ 3/3  Création du post LinkedIn...")
    status, post_urn, body = create_post(image_urn)

    if status == "201":
        print(f"\n✅ Post publié !")
        if post_urn:
            print(f"   URN    : {post_urn}")
            print(f"   Delete : DELETE /rest/posts/{post_urn}")
    else:
        print(f"\n❌ Échec — HTTP {status}")
        print(f"   {body[:500]}")


if __name__ == "__main__":
    main()

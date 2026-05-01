#!/usr/bin/env python3
"""
Publish skill-inventory video post to LinkedIn.
Run: python3 publish_video.py
"""
import os, json, subprocess, sys
from pathlib import Path

TOKEN     = os.environ["LINKEDIN_TOKEN"]
PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]

# Résout le problème NFD/NFC macOS : on cherche le fichier dynamiquement
def _find_video() -> Path:
    desktop = Path("/Users/victorrubia/Desktop")
    for f in desktop.iterdir():
        if f.suffix == ".mov" and "Enregistrement" in f.name and "19.01" in f.name:
            return f
    raise FileNotFoundError("Vidéo introuvable sur le Desktop — vérifie le nom du fichier.")

VIDEO_PATH = _find_video()

POST_TEXT = """🛠️ J'avais 205 skills Claude Code installées. Je savais plus ce que j'avais.

62 globales, 122 dans les plugins. Et ça grossit chaque semaine : de nouveaux packs, de nouveaux agents, de nouvelles skills. Tu installes, tu testes, tu oublies.

J'ai lancé un audit. Résultat : 22 skills "shadowed by plugin" à 100% de similarité. En clair, j'avais les mêmes skills en local ET via le plugin. 22 doublons purs que je trimbalais sans le savoir.

Alors j'ai créé skill-inventory, un CLI Python sans dépendance pour faire le tri.

→ audit    : difflib sur toutes les descriptions, repère les quasi-doublons
→ clean    : supprime avec backup automatique avant chaque suppression
→ match    : donne un repo GitHub, te dit ce que t'as, ce que t'as pas
→ prune    : vire les skills jamais utilisées par tes projets locaux

0 dépendance. 0 clé API. Juste Python.

Si t'as +50 skills installées et que tu sais plus où t'en es, ça peut aider.

👇 https://github.com/Victor-R-R/skill-inventory

#ClaudeCode #DeveloperTools #AI #Productivity #OpenSource"""


def run_curl(cmd: list) -> tuple:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout, r.returncode


def _parse_li_json(raw: str) -> dict:
    """Parse LinkedIn JSON that may contain newlines inside URL values."""
    import re
    # Remove literal \n inside JSON string values (base64 URLs with line breaks)
    cleaned = re.sub(r'(?<=")(\n)(?=[^"]*")', "", raw)
    # Fallback: strip all control chars except tab
    cleaned = re.sub(r'[\x00-\x08\x0b-\x1f]', "", cleaned)
    return json.loads(cleaned)


def initialize_upload(file_size: int) -> dict:
    payload = json.dumps({
        "initializeUploadRequest": {
            "owner": f"urn:li:person:{PERSON_ID}",
            "fileSizeBytes": file_size,
            "uploadCaptions": False,
            "uploadThumbnail": False,
        }
    })
    stdout, _ = run_curl([
        "curl", "-s", "-X", "POST",
        "https://api.linkedin.com/rest/videos?action=initializeUpload",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", "LinkedIn-Version: 202503",
        "-H", "X-Restli-Protocol-Version: 2.0.0",
        "-d", payload,
    ])
    try:
        return _parse_li_json(stdout)
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw (first 500): {stdout[:500]}")
        return {}


def upload_part(upload_url: str, path: Path, first_byte: int, last_byte: int) -> tuple:
    """Upload one chunk of a multipart video upload.
    Reads only the relevant bytes from the file and streams them to the pre-signed URL.
    No Authorization header — the URL is pre-signed (auth embedded).
    """
    clean_url = upload_url.replace("\n", "").replace("\r", "").strip()
    chunk_size = last_byte - first_byte + 1

    with open(path, "rb") as f:
        f.seek(first_byte)
        chunk = f.read(chunk_size)

    result = subprocess.run([
        "curl", "-s", "-i",
        "-X", "PUT", clean_url,
        "-H", "Content-Type: application/octet-stream",
        "-H", f"Content-Length: {chunk_size}",
        "--data-binary", "@-",
    ], input=chunk, capture_output=True)

    stdout = result.stdout.decode("utf-8", errors="replace")
    headers_raw, _, body = stdout.partition("\r\n\r\n")
    first_line = headers_raw.split("\r\n")[0] if headers_raw else ""
    code = first_line.split(" ")[1] if " " in first_line else "?"

    etag = next(
        (h.split(":", 1)[1].strip().strip('"') for h in headers_raw.split("\r\n")
         if h.lower().startswith("etag:")),
        None,
    )
    return code, etag, body[:400]


def finalize_upload(video_urn: str, upload_token: str, etags: list) -> str:
    payload = json.dumps({
        "finalizeUploadRequest": {
            "video": video_urn,
            "uploadToken": upload_token,
            "uploadedPartIds": etags,
        }
    })
    stdout, _ = run_curl([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST",
        "https://api.linkedin.com/rest/videos?action=finalizeUpload",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/json",
        "-H", "LinkedIn-Version: 202503",
        "-H", "X-Restli-Protocol-Version: 2.0.0",
        "-d", payload,
    ])
    return stdout.strip()


def create_post(video_urn: str) -> tuple:
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
            "media": {"id": video_urn}
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
    if not VIDEO_PATH.exists():
        print(f"❌ Fichier introuvable : {VIDEO_PATH}")
        sys.exit(1)

    file_size = VIDEO_PATH.stat().st_size
    print(f"Fichier : {VIDEO_PATH.name}")
    print(f"Taille  : {file_size / 1_000_000:.1f} MB\n")

    print("→ 1/4  Initialisation de l'upload...")
    data = initialize_upload(file_size)
    val = data.get("value", {})
    if not val or "video" not in val:
        print(f"❌ Échec initializeUpload : {json.dumps(data, indent=2)}")
        sys.exit(1)

    video_urn    = val["video"]
    upload_token = val.get("uploadToken", "")
    instructions = val.get("uploadInstructions", [])

    print(f"✓  Video URN    : {video_urn}")
    print(f"   Parts         : {len(instructions)}")
    print(f"   Upload token  : {'present' if upload_token else 'absent'}")

    if not instructions:
        print("❌ Aucune uploadInstructions reçue — abandon")
        sys.exit(1)

    print("→ 2/4  Upload vidéo multipart...")
    etags = []
    for i, part in enumerate(instructions):
        first_byte = part["firstByte"]
        last_byte  = part["lastByte"]
        print(f"   Part {i+1}/{len(instructions)} — bytes {first_byte}–{last_byte}...", end=" ", flush=True)
        code, etag, err_body = upload_part(part["uploadUrl"], VIDEO_PATH, first_byte, last_byte)
        print(f"HTTP {code} | ETag: {etag or 'none'}")
        if code not in ("200", "201", "204"):
            print(f"   ⚠️  Erreur: {err_body}")
        if etag:
            etags.append(etag)

    print("→ 3/4  Finalisation de l'upload...")
    fin_code = finalize_upload(video_urn, upload_token, etags)
    print(f"   Finalize HTTP : {fin_code}")
    if fin_code not in ("200", "201", "204"):
        print("   ⚠️  Finalisation échouée — le post sera peut-être sans vidéo")

    print("→ 4/4  Création du post LinkedIn...")
    status, post_urn, body = create_post(video_urn)

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

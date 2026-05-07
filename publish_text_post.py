import subprocess, os, json
from urllib.parse import unquote

TOKEN     = os.environ["LINKEDIN_TOKEN"]
PERSON_ID = os.environ["LINKEDIN_PERSON_ID"]

POST_TEXT = """🛠️ Ce matin je suis tombé sur un thème VSCode qui m'a donné l'impression que mon IDE venait d'être upgradé.

Islands Dark. 8 000 stars sur GitHub, et je comprends maintenant pourquoi.

Ce qui m'a surpris c'est que ce n'est pas juste un color scheme. Il injecte du CSS directement dans VSCode pour recréer des panneaux flottants, des bordures verre, des animations sur tout. Tu te retrouves avec quelque chose qui ressemble visuellement à un IDE JetBrains.

Installé en 30 secondes sur mon projet en cours. Je pense pas revenir en arrière.

👇 github.com/bwya77/vscode-dark-islands

#VSCode #OpenSource"""

payload = json.dumps({
    "author": f"urn:li:person:{PERSON_ID}",
    "commentary": POST_TEXT,
    "visibility": "PUBLIC",
    "distribution": {
        "feedDistribution": "MAIN_FEED",
        "targetEntities": [],
        "thirdPartyDistributionChannels": [],
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": False,
})

r = subprocess.run([
    "curl", "-s", "-i",
    "-X", "POST", "https://api.linkedin.com/rest/posts",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-H", "LinkedIn-Version: 202503",
    "-H", "X-Restli-Protocol-Version: 2.0.0",
    "-d", payload,
], capture_output=True, text=True)

headers_raw, _, body = r.stdout.partition("\r\n\r\n")
status = headers_raw.split("\r\n")[0].split(" ")[1] if headers_raw else "?"
post_urn = next(
    (h.split(":", 1)[1].strip() for h in headers_raw.split("\n")
     if h.lower().startswith("x-restli-id:")), None
)

if status == "201":
    print(f"✅ Post publié !")
    print(f"   URN : {post_urn}")
    print(f"   Delete : DELETE /rest/posts/{post_urn}")
else:
    print(f"❌ HTTP {status}")
    print(body[:400])

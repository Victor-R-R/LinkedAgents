import subprocess, os
from urllib.parse import quote

TOKEN = os.environ["LINKEDIN_TOKEN"]
URN = "urn:li:share:7457705280966021120"
URN_ENCODED = quote(URN, safe="")

r = subprocess.run([
    "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
    "-X", "DELETE",
    f"https://api.linkedin.com/rest/posts/{URN_ENCODED}",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "LinkedIn-Version: 202503",
    "-H", "X-Restli-Protocol-Version: 2.0.0",
], capture_output=True, text=True)

print(f"HTTP {r.stdout.strip()}")
if r.stdout.strip() == "204":
    print("✅ Post supprimé")
else:
    print("❌ Échec — vérifie le token ou l'URN")

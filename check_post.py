import subprocess, os, json

TOKEN = os.environ["LINKEDIN_TOKEN"]
URN = "urn%3Ali%3Ashare%3A7457705280966021120"

r = subprocess.run([
    "curl", "-s",
    f"https://api.linkedin.com/rest/posts/{URN}",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "LinkedIn-Version: 202503",
    "-H", "X-Restli-Protocol-Version: 2.0.0",
], capture_output=True, text=True)

try:
    print(json.dumps(json.loads(r.stdout), indent=2)[:1000])
except:
    print(r.stdout[:800])

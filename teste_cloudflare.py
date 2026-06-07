import base64
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")

if not TOKEN or not ACCOUNT:
    print("ERRO: preencha CLOUDFLARE_API_TOKEN e CLOUDFLARE_ACCOUNT_ID no arquivo .env")
    sys.exit(1)

BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/ai/run"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

TEXTO = "Varsóvia. A cidade que recusa morrer. O Vístula corre escuro esta noite, e os mortos que sobreviveram à guerra ainda se lembram do cheiro das cinzas."


def gerar_audio(lang: str, saida: str):
    r = requests.post(
        f"{BASE}/@cf/myshell-ai/melotts",
        headers=HEADERS,
        json={"prompt": TEXTO, "lang": lang},
        timeout=60,
    )
    if r.status_code != 200:
        print(f"  ERRO {r.status_code}: {r.text[:200]}")
        return
    audio = base64.b64decode(r.json()["result"]["audio"])
    with open(saida, "wb") as f:
        f.write(audio)
    print(f"  {saida} ({len(audio):,} bytes)")


if __name__ == "__main__":
    print("Gerando amostras de voz em português...\n")
    gerar_audio("pt", "voz_melotts_pt.wav")
    gerar_audio("pt-BR", "voz_melotts_ptbr.wav")
    print("\nOuça os dois e diga se a qualidade está boa para integrar no Flask.")

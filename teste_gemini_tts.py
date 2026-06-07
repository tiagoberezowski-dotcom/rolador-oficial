import os
import sys
import wave
import struct
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    print("ERRO: GOOGLE_API_KEY não encontrada no .env")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

TEXTO = (
    "Varsóvia. A cidade que recusa morrer. "
    "O Vístula corre escuro esta noite, e os mortos que sobreviveram à guerra "
    "ainda se lembram do cheiro das cinzas."
)

# Vozes disponíveis para pt-BR no demo do Google
# Vozes selecionadas para atmosfera VTM (gótico, sombrio, misterioso)
VOZES = [
    ("Charon",  "vtm_charon.wav"),    # informative — o barqueiro dos mortos
    ("Algenib", "vtm_algenib.wav"),   # gravelly — rouco, sombrio
    ("Gacrux",  "vtm_gacrux.wav"),    # mature — aristocrático
    ("Schedar", "vtm_schedar.wav"),   # even — narrador frio e implacável
    ("Fenrir",  "vtm_fenrir.wav"),    # excitable — dramático para cenas de tensão
]


def salvar_wav(pcm_bytes: bytes, nome: str, sample_rate: int = 24000):
    with wave.open(nome, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    print(f"  {nome} ({len(pcm_bytes):,} bytes)")


def gerar(voz: str, nome: str):
    response = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=TEXTO,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voz
                    )
                )
            ),
        ),
    )
    part = response.candidates[0].content.parts[0]
    data = part.inline_data.data
    if "wav" in part.inline_data.mime_type:
        open(nome, "wb").write(data)
        print(f"  {nome} ({len(data):,} bytes WAV)")
    else:
        salvar_wav(data, nome)


if __name__ == "__main__":
    print("Modelo: gemini-3.1-flash-tts-preview\n")
    for voz, nome in VOZES:
        print(f"Gerando: {voz}")
        try:
            gerar(voz, nome)
        except Exception as e:
            print(f"  ERRO: {e}")
    print("\nOuça e escolha a voz favorita para integrar no Flask.")

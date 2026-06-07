import asyncio
import edge_tts

TEXTO = (
    "Então vocês chegam até o galpão. Há algo pesado lá dentro; "
    "vocês não sabem exatamente o quê, mas sentem sua presença. "
    "Do lado de fora, o frio está intenso, e há apenas uma pequena janela "
    "que levaria vocês para dentro do galpão. Vocês aceitam entrar?"
)

VOZES_PT_BR = [
    "pt-BR-AntonioNeural",
    "pt-BR-FranciscaNeural",
    "pt-BR-ThalitaNeural",
    "pt-BR-ThalitaMultilingualNeural",
    "pt-BR-MacerioMultilingualNeural",
]


async def gerar(voz: str):
    nome = f"teste_{voz}.mp3"
    communicate = edge_tts.Communicate(TEXTO, voz)
    await communicate.save(nome)
    print(f"  Salvo: {nome}")


async def main():
    print("Gerando amostras de voz pt-BR...\n")
    for voz in VOZES_PT_BR:
        print(f"Gerando: {voz}")
        try:
            await gerar(voz)
        except Exception as e:
            print(f"  ERRO: {e}")
    print("\nPronto! Ouça os arquivos .mp3 e escolha a voz.")

if __name__ == "__main__":
    asyncio.run(main())

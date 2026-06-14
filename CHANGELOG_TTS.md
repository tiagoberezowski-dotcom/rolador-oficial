# Changelog — Correção e Melhorias do Narrador TTS

**Data:** 2026-06-08
**Projeto:** Rolador Oficial — Crônica de Varsóvia (VTM 5E)
**Objetivo:** Corrigir o narrador TTS que não narrava o texto completo + adicionar streaming de áudio + redesign do player.

---

## Diagnóstico

O botão "▶ OUVIR" nas mensagens do Mestre usa `edge-tts` (Microsoft TTS, voz `pt-BR-ThalitaNeural`) para narrar o texto. Foram encontrados 5 problemas + 1 melhoria:

| # | Tipo | Severidade | Problema | Arquivo |
|---|---|---|---|---|
| P1 | Bug | 🔴 Crítico | Frontend destruía quebras de parágrafo (`<br>` virava espaço) | `templates/index.html` |
| P2 | Bug | 🟠 Alto | Truncamento em 3000 chars não respeitava fim de frase | `app.py` |
| P3 | Bug | 🟡 Médio | Blocos de diálogo de NPC não tinham botão "OUVIR" | `templates/index.html` |
| P4 | Limpeza | ⚪ Baixo | Código morto/zumbi (rota duplicada + função inexistente) | `app.py` |
| P5 | Bug | ⚪ Baixo | Streaming (`/stream_chat`) não adicionava botão TTS ao terminar | `templates/index.html` |
| P6 | Melhoria | 🔵 Feature | Áudio só começava a tocar após download completo | `templates/index.html` |
| P7 | Melhoria | 🟣 Design | Player visual pobre — botões inline sem estilo | `templates/index.html` |

---

## Correções aplicadas

### P1 — Frontend: preservar quebras de linha ao limpar HTML

**Antes:**
```javascript
const textoPlano = textoComTags.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
```
Isso convertia `<br>` em espaço, colapsando parágrafos inteiros num bloco único.

**Depois:**
```javascript
const textoPlano = textoComTags
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<hr[^>]*>/gi, '\n\n')
    .replace(/<[^>]+>/g, '')
    .replace(/ {2,}/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
```
Agora `<br>` vira `\n`, `<hr>` vira `\n\n`, e só depois as demais tags são removidas.

---

### P2 — Backend: melhorar truncamento

**Antes:**
- `LIMITE_CHARS = 3000`
- Fallback não considerava `.\n` como fim de frase
- Não contabilizava os `\n\n` no cálculo de comprimento

**Depois:**
- `LIMITE_CHARS = 5000`
- Fallback busca também `.\n` como delimitador
- Cálculo de parágrafos inclui `+ 2` para os `\n\n`

---

### P3 — Adicionar botão TTS nos blocos de diálogo de NPC

**Antes:** A lógica de criação dos botões "▶ OUVIR" e "⏸" estava inline dentro de `criarMsgDiv()`. Os blocos de NPC (renderizados via `[NPC: Nome]`) não usavam `criarMsgDiv()`, portanto nunca recebiam botão.

**Depois:**
1. Extraída função auxiliar `adicionarBotoesTTS(containerEl, textoHTML)`
2. Constante `TTS_BTN_STYLE` reutilizável
3. `criarMsgDiv()` agora chama `adicionarBotoesTTS()`
4. Blocos de NPC no `carregarChat()` também chamam `adicionarBotoesTTS()`

---

### P4 — Remover código morto

**Arquivo:** `app.py:2321-2358`

Removidas 38 linhas de código inalcançável:
- Segunda definição `@app.route('/tts')` dentro da primeira função `tts()` (registrava rota duplicada)
- Chamada a `asyncio.run(_gerar())` — função que não existe no código

---

### P5 — Botão TTS ao fim do streaming

**Antes:** Quando o stream do Mestre terminava (`data.done`), o texto era exibido sem botão TTS. O botão só aparecia no próximo ciclo de polling.

**Depois:**
- Array `npcBlocosStream` rastreia os blocos de NPC criados durante o stream
- No `data.done`, `adicionarBotoesTTS()` é chamado no div do Mestre e em todos os blocos de NPC acumulados
- O array é limpo após a injeção

---

### P6 — Streaming de áudio com MediaSource

**Antes:** O frontend fazia `fetch('/tts') → blob → Audio(url)` — o usuário precisava esperar TODO o áudio baixar antes de ouvir qualquer coisa. Para textos longos, isso significava 10-20 segundos de silêncio com "⏳ CARREGANDO...".

**Depois:** O frontend usa `MediaSource Extensions` para fazer streaming do áudio:

1. **Fluxo:**
   - `fetch('/tts')` inicia — o backend já fazia streaming via `edge_tts.Communicate.stream()`, entregando chunks de áudio incrementalmente
   - `MediaSource.addSourceBuffer('audio/mpeg')` recebe cada chunk
   - No primeiro `updateend` do buffer, o `<audio>` já começa a tocar
   - Os chunks seguintes são enfileirados e alimentados conforme o buffer processa

2. **Fallback automático:** Se o navegador não suportar `MediaSource` ou o codec `audio/mpeg`, cai para o comportamento antigo (blob completo)

3. **Controles mantidos:**
   - ▶ OUVIR → inicia o stream
   - ■ PARAR → aborta o fetch e para o áudio
   - ⏸ / ▶ → pausa/continua normalmente
   - Ao final do áudio, botão volta ao estado original

4. **Novas funções auxiliares:**
   - `_ttsLimparAudio()` — para qualquer áudio/stream anterior, restaura estado dos botões
   - `_ttsFallbackBlob()` — fallback para navegadores sem MediaSource
   - `_ttsAbort` — `AbortController` para cancelar streaming em andamento

---

### P7 — Redesign do player TTS (minimalista, dourado, fino)

**Antes:** Dois botões inline simples — "▶ OUVIR" com texto e "⏸" escondido:
- Visual: retângulo sem graça, cor `#888`, borda `#444`
- Sem indicador de progresso
- Sem indicador de tempo

**Depois:** Player inline completo dentro de `.tts-player`:

```
[▶] [▬▬▬▬▬▬▬░░░░░] [0:23] [⏸]
```

- **Botões circulares** — `border-radius: 50%`, 26x26px, borda dourada `var(--borda-ouro)`, ícone na cor `var(--ouro)`
- **Hover** — background dourado translúcido, borda clara
- **Track de progresso** — barra fina de 2px com preenchimento dourado
- **Tempo** — label `m:ss` em fonte Inter, cor `#666`
- **Animação de loading** — pulso no ícone ▶ com `tts-pulse`
- **Transições** — todos os estados com `transition: 0.25s ease`
- **Estrutura do DOM:**
  ```html
  <div class="tts-player ativo" data-tts-text="...">
    <button class="tts-btn tts-btn-play">▶</button>
    <div class="tts-track-wrap">
      <span class="tts-track"><span class="tts-progress"></span></span>
      <span class="tts-time"></span>
    </div>
    <button class="tts-btn tts-btn-pause">⏸</button>
  </div>
  ```

- **Estados do player:**
  - **Inativo:** só ▶ visível
  - **Carregando:** ▶ vira ◌ com animação de pulso
  - **Tocando:** ▶ vira ■, aparece track + tempo + ⏸; barra de progresso avança
  - **Ao final:** barra chega 100%, tempo congela, 600ms depois reseta para estado inativo

---

## Verificação

Para testar as correções:

1. **Iniciar o servidor:** `cd "Rolador Oficial - cópia" && python3 app.py`
2. **Abrir no navegador:** `http://localhost:5000`
3. **Fazer login** como Lior ou Fryderyk
4. **Enviar uma mensagem** ao Mestre que gere resposta longa (com múltiplos parágrafos e diálogos de NPC)
5. **Clicar "▶ OUVIR"** e verificar:
   - O áudio **começa a tocar quase imediatamente** (sem esperar download completo)
   - O áudio narra o texto **até o final** (sem truncamento)
   - Blocos de NPC também exibem botão "▶ OUVIR"
   - O botão aparece imediatamente após o streaming terminar
   - Botão ■ PARAR interrompe o áudio corretamente
   - Botão ⏸ pausa/continua funciona

---

## Impacto em outras funcionalidades

**Nenhum.** As alterações são estritamente localizadas:

- **Frontend:** apenas a função `reproduzirTTS()` e os pontos de criação de botões TTS foram modificados. O fluxo do chat, rolagem de dados, fichas e SSE não foram alterados.
- **Backend:** apenas o endpoint `/tts` (truncamento + remoção de código morto). O restante do `app.py` (~2300 linhas) permanece inalterado.
- **Banco de dados:** sem alterações.

# Changelog — Rolador Oficial

**Data:** 2026-06-08
**Projeto:** Rolador Oficial — Crônica de Varsóvia (VTM 5E)

---

## 1. Correção do Narrador TTS

### 1.1 — Frontend: preservar quebras de linha ao limpar HTML
**Arquivo:** `templates/index.html`, função `reproduzirTTS()`

O regex `textoComTags.replace(/<[^>]+>/g, ' ')` convertia `<br>` em espaço, colapsando parágrafos inteiros num bloco único. O backend dependia de `\n\n` para identificar parágrafos e truncar corretamente.

**Correção:** Substituir `<br>` → `\n` e `<hr>` → `\n\n` antes de remover as demais tags HTML.

```javascript
const textoPlano = textoComTags
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<hr[^>]*>/gi, '\n\n')
    .replace(/<[^>]+>/g, '')
    .replace(/ {2,}/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
```

### 1.2 — Backend: streaming de áudio + melhor truncamento
**Arquivo:** `app.py`, endpoint `/tts`

- `LIMITE_CHARS` aumentado de 3000 → 5000
- Fallback melhorado para respeitar fim de frase (inclui `.\n`)
- Parágrafos acumulados com `+ 2` para contabilizar os `\n\n`
- Backend convertido de blob (`asyncio.run`) para streaming (`Response(_sync_gen())`)

### 1.3 — Remoção de código morto
**Arquivo:** `app.py:2321-2358`

Removidas 38 linhas de código inalcançável: rota `/tts` duplicada dentro da primeira + chamada a `_gerar()` inexistente.

---

## 2. Prompt do Mestre — proibição de markdown na narração

**Arquivo:** `app.py`, prompt do sistema

Duas proibições adicionadas:
- Na seção **"Sua voz"** (linha 576): "Nunca use markdown na narração — sem `**`, `*`, `###` ou `` ` ``"
- No item #12 de **"O QUE NUNCA FAZER"**: "A prosa não tem cerquilha, asteriscos nem código inline"

---

## 3. Regras de XP — correção para fórmula oficial V5

**Arquivos:** `app.py` (`_custo_xp`), `templates/index.html` (`custoXP`)

**Antes:** custo fixo (Atributo=5, Skill=3, Disciplina in-clã=3, out-clã=5)

**Depois:** fórmula oficial — custo = `nível novo × multiplicador`

| Tipo | Multiplicador |
|---|---|
| Atributo | × 5 |
| Skill | × 3 |
| Disciplina in-clã | × 5 |
| Disciplina out-clã | × 7 |

---

## 4. Reset das fichas + importação dos PDFs oficiais

### 4.1 — Reset completo
Ambas as fichas zeradas (47 stats = 0), XP = 0, recursos padrão (WP=5, Health=3, Humanity=7).

### 4.2 — Lior Kovalenko (PDF: `lior_att.pdf`)
**Atributos:** Str 1, Dex 3, Sta 2, Cha 2, Man 2, Com 2, Int 4, Wit 3, Res 3
**Disciplinas:** Auspex 2, Obfuscate 4
**Skills principais:** Technology 4, Firearms 3, Stealth 3, Streetwise 3, Academics 2, Awareness 2, Finance 2
**Especialidades:** Academics → Research, Craft → Design, Stealth → Break-in, Technology → Hacking
**Recursos:** Willpower 5, Health 3, Humanity 7
**XP:** total 35 gasto, 0 disponível

### 4.3 — Fryderyk Rozynski (PDF: `fri.pdf`)
**Atributos:** Str 1, Dex 2, Sta 2, Cha 4, Man 3, Com 3, Int 3, Wit 2, Res 2
**Disciplinas:** Presence 3, Auspex 2, Dominate 1
**Skills principais:** Persuasion 3, Politics 3, Investigation 3, Performance 2, Academics 2, Awareness 2, Etiquette 2, Finance 2, Insight 2, Intimidation 2, Subterfuge 2
**Especialidades:** Academics → Arts, Performance → Harpsichord, Politics → Diplomacy, Science → Engineering
**Recursos:** Willpower 5, Health 5, Humanity 6
**XP:** total 35 gasto, 0 disponível

---

## 5. Header do personagem — redesign completo UX/UI

### 5.1 — Estrutura unificada (character-banner)
**Arquivos:** `templates/index.html`, `app.py`

Todo o topo da página foi redesenhado como um banner único com borda dourada contínua, eliminando os antigos `.avatar-container`, `.fome-tracker` e `.recursos-panel` separados.

```
┌─character-banner (borda dourada, radius 10px)────────────┐
│ ┌──────────────────────────────────────────────────────┐ │
│ │              CAPA (900×160px)                        │ │
│ │         [✧ ALTERAR CAPA no hover]                   │ │
│ │         [ARRASTE PARA AJUSTAR]                       │ │
│ └──────────────────────────────────────────────────────┘ │
│                   ┌──────────┐                           │
│                   │   FOTO   │ ← avatar 130px circular   │
│                   │  130px   │   sobrepondo a capa        │
│                   └──────────┘                           │
│                                                          │
│               LIOR KOVALENKO                             │
│        Malkavian · Ancilla · Sandman                     │
│                                                          │
│  ──────────────────────────────────────────────────────  │
│  HUNGER | WILLPOWER | HEALTH | HUMANITY | BANE | RESONANCE │
│   0/5   |    5      |   3    |    7    | Fract.|  None   │
│  ○○○○○  |   − +     |  − +   |   − +   | Persp.|         │
└──────────────────────────────────────────────────────────┘
```

### 5.2 — CSS novo
- `.character-banner` — wrapper único com `border: 1px solid var(--borda-ouro)`, `border-radius: 10px`, `overflow: visible`
- `.capa-container` — 160px altura, `border-bottom` como divisor interno, `border-radius: 10px 10px 0 0`
- `.avatar-section` — `margin-top: -50px; z-index: 2` sobrepondo a borda da capa
- `.avatar-circle` — 130px, `box-shadow: 0 0 0 8px var(--bg)` simulando recorte do fundo
- `.personagem-card` — padding 60px no topo (espaço pro avatar), sem borda própria
- `.personagem-trackers` — `flex-wrap: nowrap`, `gap: 14px`, 6 badges em linha única
- `.personagem-badge` — `flex-shrink: 0`, labels 0.55rem, valores 0.95rem

### 5.3 — Capa: upload + crop + reposicionamento
**Upload:** `processarUploadCapa()` faz crop centralizado na proporção 5.6:1 (1800×320px), JPEG qualidade 0.9, `imageSmoothingQuality: 'high'`.

**Reposicionamento por arraste:** Ao clicar e arrastar verticalmente sobre a capa, o `background-position` Y é ajustado em tempo real. Se for um clique sem arraste (>3px), abre o seletor de arquivo. Funciona com mouse e touch.

**Persistência:** `capaOffsetY` salvo em `localStorage` por personagem (`vtm_capa_offset_Lior` / `vtm_capa_offset_Fryderyk`).

**Overlay:** "✧ ALTERAR CAPA" aparece no hover. "ARRASTE PARA AJUSTAR" aparece como dica.

### 5.4 — Isolamento por personagem (localStorage)
**Arquivo:** `templates/index.html`

Função `_lsKey(base)` gera chaves por jogador:
- `vtm_ficha_viva_Lior` / `vtm_ficha_viva_Fryderyk`
- `vtm_especialidades_Lior` / `vtm_especialidades_Fryderyk`
- `vtm_avatar_url_Lior` / `vtm_avatar_url_Fryderyk`
- `vtm_capa_url_Lior` / `vtm_capa_url_Fryderyk`
- `vtm_capa_offset_Lior` / `vtm_capa_offset_Fryderyk`

Cada personagem vê apenas seus próprios dados — sem vazamento entre Lior e Fryderyk.

### 5.5 — Backend para capa
**Arquivo:** `app.py`

- Migration: coluna `capa TEXT` adicionada à tabela `fichas`
- Endpoint `GET /ficha` retorna `capa` no JSON (junto com `avatar`)
- Endpoint `POST /avatar` aceita também `capa` no payload
- `POST /ficha` remove `capa` do JSON antes de salvar (persiste separado)

### 5.6 — Campos Bane e Resonance
**Arquivos:** `app.py` (rota `/`), `templates/index.html` (template)

Dois novos badges na barra de trackers:
- **Bane:** `Fractured Perspective` (Lior) / `Aesthetic Fixation` (Fryderyk)
- **Resonance:** `None` (ambos, placeholder para evoluir na crônica)

---

## 6. Nome completo + linha de informação

**Arquivos:** `app.py` (rota `/`), `templates/index.html` (template)

Rota `/` agora passa ao template:
- `nome` — nome completo (`Lior Kovalenko` / `Fryderyk Rozynski`)
- `info` — clã, idade, predador (`Malkavian · Ancilla · Sandman`)
- `bane` — maldição de clã
- `resonance` — ressonância atual

Template renderiza `{{ nome }}` em vez de `{{ jogador | upper }}`.

---

## 7. Visual das disciplinas — alinhamento com o resto da ficha

**Arquivo:** `templates/index.html`, CSS `.disc-header`

O header das disciplinas usava borda sempre visível e padding maior que os `.stat-row`. Corrigido para:
- `border: 1px solid transparent` (como `.stat-row`)
- `padding: 6px 8px` (idêntico)
- Toggle ▸ e botão ADQUIRIR com `opacity: 0` → visíveis só no hover

---

## 8. Correção de inicialização — especialidades

**Arquivo:** `templates/index.html`

Ordem de inicialização corrigida: `inicializarFicha()` renderiza do cache primeiro, depois `carregarFichaServidor()` sobrescreve com dados do banco. Evita que especialidades sumam ao trocar de navegador.

---

## Arquivos modificados

| Arquivo | Mudanças |
|---|---|
| `app.py` | TTS: streaming + limite 5000 + código morto removido; Prompt: proibição de markdown; XP: fórmula oficial; Ficha: capa + migration + endpoint; Index: nome + info + bane + resonance |
| `templates/index.html` | TTS: regex de parágrafos; Header: banner completo (capa + avatar + card + trackers + bane + resonance); XP: fórmula oficial; Disciplinas: CSS alinhado; localStorage: chaves por jogador; Capa: upload com crop + reposicionamento por arraste; Inicialização: ordem corrigida |
| `CHANGELOG.md` | Este arquivo |
| `CHANGELOG_TTS.md` | Changelog antigo (mantido como histórico) |

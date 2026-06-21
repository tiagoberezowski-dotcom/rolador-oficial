# Deploy & Infraestrutura — Rolador Oficial

App Flask de RPG colaborativo (VtM 5e).

## Servidor atual (desde jun/2026)

Hospedado em VM própria no **Google Cloud Platform**.

| Item | Valor |
|------|-------|
| Projeto GCP | `agenda-auto-498817` |
| VM | `instance-20260613-064555` (e2-micro, free tier) |
| Zona | `us-central1-a` |
| IP externo | `146.148.51.209` |
| Usuário | `tiagoberezowski` |
| Código | `/home/tiagoberezowski/rolador-oficial/` |
| Serviço | `rolador.service` (systemd + gunicorn, `--workers 2 --threads 8`, bind `127.0.0.1:5001`) |
| Proxy | nginx → `proxy_pass http://127.0.0.1:5001` |
| Domínio | `berezowski.dev` / `www.berezowski.dev` (HTTPS) |
| Banco | SQLite em `/home/tiagoberezowski/rolador-oficial/banco.db` |

> A mesma VM é o "site do Tiago" no free tier forever — **não desligar nem apagar**.

## Repositório

```
git@github.com:tiagoberezowski-dotcom/rolador-oficial.git
```

## Como fazer deploy

1. Commitar e enviar do Mac:
   ```bash
   git push
   ```
2. Conectar no servidor:
   ```bash
   gcloud compute ssh instance-20260613-064555 \
     --zone=us-central1-a --project=agenda-auto-498817
   ```
3. Atualizar e reiniciar:
   ```bash
   cd ~/rolador-oficial
   git pull
   sudo systemctl restart rolador.service
   ```
4. Conferir que subiu:
   ```bash
   systemctl is-active rolador.service
   curl -sI https://berezowski.dev/login   # deve dar HTTP 200
   ```

> Acessar pelo **IP cru** (`146.148.51.209`) dá **404** — é esperado: o nginx
> serve o app só no `server_name berezowski.dev`; o IP cai no `default_server`.
> Sempre teste pelo domínio.

## Configuração do servidor (systemd + .env)

O unit do systemd está versionado em [`deploy/rolador.service`](deploy/rolador.service). Ao recriar a VM, copiar para `/etc/systemd/system/rolador.service` e rodar `sudo systemctl daemon-reload && sudo systemctl enable --now rolador.service`.

**gunicorn usa `--workers 2 --threads 8` (worker class `gthread`).** As threads são essenciais: o endpoint `/eventos` é SSE de verdade e segura uma conexão aberta por jogador; com workers sync sem threads, 2 jogadores conectados saturavam os 2 workers e o app travava pra todos.

**`.env` (NÃO versionado — gitignored) — chaves usadas pelo `app.py`:**

- `SECRET_KEY` — obrigatória (sem ela o app nem sobe)
- `SENHA_MESTRE` — senha do painel admin / reset / XP
- `DEEPSEEK_API_KEY` — Mestre IA
- `GROQ_API_KEY` (e opcionais `BRIEFING_API_KEY` / `BRIEFING_BASE_URL` / `BRIEFING_MODEL`) — briefing/preparador de cena (Groq/Llama); sem nenhuma chave, o briefing fica desligado
- `GOOGLE_API_KEY` — Gemini
- `DB_PATH` — caminho do SQLite (opcional; default é `banco.db` na pasta do projeto)
- `R2_ACCOUNT_ID` / `R2_ACCESS_KEY` / `R2_SECRET_KEY` / `R2_BUCKET` / `R2_PUBLIC_URL` — storage de imagens no Cloudflare R2; se ausentes, avatares/capas ficam inline (base64) no banco

> Como o `.env` não é levado pelo `git pull`, ao adicionar features que usam chaves novas, **atualizar o `.env` do servidor manualmente** antes de reiniciar.

## Comandos úteis no servidor

```bash
# Status / logs
systemctl status rolador.service
journalctl -u rolador.service -n 100 --no-pager

# Reiniciar nginx
sudo systemctl restart nginx
```

## Fix de emergência — mensagens voltando após limpar o chat

O chat persiste em 3 camadas: banco SQLite (`mensagens`), `backup_mensagens.json`
e lista em RAM. Se ao reiniciar as mensagens "ressuscitam", apague o backup e
reinicie:

```bash
rm ~/rolador-oficial/backup_mensagens.json
sudo systemctl restart rolador.service
```

## Host antigo (aposentado)

DigitalOcean VPS `159.223.114.55` (código em `/root/rolador-oficial/`).
Migrado para o GCP em jun/2026. A VPS ainda pode responder ao SSH, mas **não
serve mais** o app.

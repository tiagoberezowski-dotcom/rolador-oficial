# Rolador Oficial — contexto do projeto

App Flask de RPG colaborativo (Vampire: the Masquerade 5e).
Backend em `app.py` (Flask + gunicorn), banco SQLite, templates em `templates/`.
Inclui rolador de dados, chat, narrador TTS e um "Mestre IA".

## Infraestrutura (resumo — detalhes em DEPLOY.md)

Hospedado em VM própria no **Google Cloud** (migrado da DigitalOcean em jun/2026).

- **VM:** GCP e2-micro `instance-20260613-064555`, projeto `agenda-auto-498817`, zona `us-central1-a`, IP `146.148.51.209` (free tier — **não desligar/apagar**).
- **Domínio:** https://berezowski.dev (e `www.`). Acessar pelo IP cru dá 404 — nginx só serve no `server_name berezowski.dev`; teste sempre pelo domínio.
- **Stack no servidor:** nginx → gunicorn em `127.0.0.1:5001` (2 workers) → `app:app`, sob `rolador.service` (systemd). Código em `/home/tiagoberezowski/rolador-oficial/`.
- **Repo:** `git@github.com:tiagoberezowski-dotcom/rolador-oficial.git`.

### Deploy
```bash
git push                                   # do dev para o GitHub
gcloud compute ssh instance-20260613-064555 --zone=us-central1-a --project=agenda-auto-498817
cd ~/rolador-oficial && git pull && sudo systemctl restart rolador.service
```
Ver `DEPLOY.md` para passo a passo completo, comandos úteis e fix de emergência.

## Pontos de atenção

- **Chat "ressuscitando" mensagens após limpar:** persistência em 3 camadas (SQLite, `backup_mensagens.json`, RAM). Ao limpar, apagar banco/RAM primeiro e só então zerar o backup — nunca salvar o backup antes de limpar. Fix de emergência no servidor: `rm ~/rolador-oficial/backup_mensagens.json && sudo systemctl restart rolador.service`.
- **Segredos** ficam em `.env` (gitignored): chaves de DeepSeek, Groq, briefing, Cloudflare, Google, `SECRET_KEY`, `SENHA_MESTRE`. Nunca commitar.
- `banco.db`, `.env`, `.venv/`, `.claude/` e `AUDIOS DESCARTE/` são gitignored.

## Convenções

- Mensagens de commit em português, estilo conventional commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Texto do projeto e respostas em português; evitar travessão (—).

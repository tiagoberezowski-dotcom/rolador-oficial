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
| Serviço | `rolador.service` (systemd + gunicorn) |
| Proxy | nginx |
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
   ```

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

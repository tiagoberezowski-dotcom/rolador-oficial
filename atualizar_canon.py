"""
Substitui o cânone base no banco de dados pelo CANON_INICIAL atualizado do app.py.
Execute UMA VEZ após atualizar o CANON_INICIAL em app.py.

Preserva sessões adicionais (=== SESSÃO N ===) que já estejam no banco.
"""
import sqlite3
import re
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'banco.db')

# Lê o CANON_INICIAL diretamente do app.py sem importar o módulo
def ler_canon_inicial(caminho_app):
    with open(caminho_app, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    m = re.search(r'CANON_INICIAL\s*=\s*"""(.*?)"""', conteudo, re.DOTALL)
    if not m:
        print("CANON_INICIAL não encontrado em app.py")
        sys.exit(1)
    return m.group(1)

CANON_INICIAL = ler_canon_inicial(os.path.join(os.path.dirname(__file__), 'app.py'))

def migrar():
    if not os.path.exists(DB_PATH):
        print("banco.db não encontrado. O servidor nunca foi iniciado?")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    row = con.execute('SELECT conteudo FROM canon WHERE id = 1').fetchone()

    if not row:
        print("Nenhum cânone encontrado no banco. Inserindo novo...")
        con.execute('INSERT INTO canon (id, conteudo) VALUES (1, ?)', (CANON_INICIAL,))
        con.commit()
        con.close()
        print("Feito.")
        return

    canon_atual = row[0]

    # Extrai blocos de sessão que já estejam no banco (=== SESSÃO N ===)
    sessoes = re.findall(r'\n*=== SESS[AÃ]O \d+.*', canon_atual, flags=re.DOTALL)
    sessoes_texto = '\n\n'.join(s.strip() for s in sessoes) if sessoes else ''

    # Monta o novo cânone: base atualizada + sessões preservadas
    novo_canon = CANON_INICIAL
    if sessoes_texto:
        novo_canon = novo_canon + '\n\n' + sessoes_texto

    con.execute('UPDATE canon SET conteudo = ? WHERE id = 1', (novo_canon,))
    con.commit()
    con.close()

    print(f"Cânone atualizado com sucesso.")
    if sessoes_texto:
        print(f"Sessões preservadas: {len(sessoes)} bloco(s).")
    else:
        print("Nenhuma sessão adicional encontrada no banco.")

if __name__ == '__main__':
    migrar()

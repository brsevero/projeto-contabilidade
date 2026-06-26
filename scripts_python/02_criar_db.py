"""
UTI dos nerds – Script 02: Criar Banco de Dados SQLite
Disciplina: SISB090 – Informação Contábil para Gestão
"""

import sqlite3
import pandas as pd
import os

ARQUIVO_CSV = "lancamentos_limpos.csv"
ARQUIVO_DB  = "utidosnerds.db"

print("=" * 60)
print("  UTI dos Nerds – Criação do Banco de Dados SQLite")
print("=" * 60)

if not os.path.exists(ARQUIVO_CSV):
    raise FileNotFoundError(
        "Execute primeiro o script 01_importar.py para gerar o CSV."
    )

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONECTAR AO BANCO (cria se não existir)
# ─────────────────────────────────────────────────────────────────────────────
conn = sqlite3.connect(ARQUIVO_DB)
cursor = conn.cursor()
print(f"\n🗄  Banco de dados: {ARQUIVO_DB}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. CRIAR TABELAS
# ─────────────────────────────────────────────────────────────────────────────
schema = """
DROP TABLE IF EXISTS lancamentos;
DROP TABLE IF EXISTS plano_contas;

CREATE TABLE lancamentos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    mes           TEXT,
    n_lancamento  TEXT,
    data          TEXT    NOT NULL,
    doc           TEXT,
    descricao     TEXT    NOT NULL,
    conta_debito  TEXT    NOT NULL,
    conta_credito TEXT    NOT NULL,
    valor         REAL    NOT NULL CHECK(valor > 0)
);

CREATE TABLE plano_contas (
    codigo   TEXT    PRIMARY KEY,
    conta    TEXT    NOT NULL UNIQUE,
    natureza TEXT    NOT NULL,
    tipo     TEXT    NOT NULL
);
"""

conn.executescript(schema)
print("✅ Tabelas criadas.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. POPULAR LANÇAMENTOS
# ─────────────────────────────────────────────────────────────────────────────
df = pd.read_csv(ARQUIVO_CSV, dtype=str)
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
df["data"]  = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")

df.to_sql("lancamentos", conn, if_exists="replace", index=False)

cursor.execute("SELECT COUNT(*) FROM lancamentos")
qtd = cursor.fetchone()[0]
print(f"✅ Lançamentos inseridos: {qtd}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. POPULAR PLANO DE CONTAS
# ─────────────────────────────────────────────────────────────────────────────
plano = [
    ("1.1.01","Caixa",               "Ativo Circulante",    "Devedora"),
    ("1.1.02","Banco",               "Ativo Circulante",    "Devedora"),
    ("1.1.03","Clientes",            "Ativo Circulante",    "Devedora"),
    ("1.1.04","Adiantamentos",       "Ativo Circulante",    "Devedora"),
    ("1.2.01","Equipamentos de TI",  "Ativo Nao Circulante","Devedora"),
    ("1.2.02","Moveis e Utensilios", "Ativo Nao Circulante","Devedora"),
    ("1.2.03","Depreciacao Acumulada","Ativo Nao Circulante","Credora"),
    ("2.1.01","DAS a Recolher",      "Passivo Circulante",  "Credora"),
    ("2.1.02","FGTS a Recolher",     "Passivo Circulante",  "Credora"),
    ("2.1.03","INSS a Recolher",     "Passivo Circulante",  "Credora"),
    ("2.1.04","Salarios a Pagar",    "Passivo Circulante",  "Credora"),
    ("2.1.05","Fornecedores",        "Passivo Circulante",  "Credora"),
    ("3.1.01","Capital Social",      "Patrimonio Liquido",  "Credora"),
    ("3.2.01","Lucros Acumulados",   "Patrimonio Liquido",  "Credora"),
    ("4.1.01","Rec. Servicos",       "Resultado Receita",   "Credora"),
    ("5.1.01","Desp. Salarios",      "Resultado Despesa",   "Devedora"),
    ("5.1.02","Desp. FGTS",          "Resultado Despesa",   "Devedora"),
    ("5.1.03","Desp. INSS Patronal", "Resultado Despesa",   "Devedora"),
    ("5.1.04","Desp. Pro-labore",    "Resultado Despesa",   "Devedora"),
    ("5.1.05","Desp. Aluguel",       "Resultado Despesa",   "Devedora"),
    ("5.1.06","Desp. Telecom",       "Resultado Despesa",   "Devedora"),
    ("5.1.07","Desp. Mat. Escritorio","Resultado Despesa",  "Devedora"),
    ("5.1.08","Desp. Depreciacao",   "Resultado Despesa",   "Devedora"),
    ("5.1.09","Desp. Tributos",      "Resultado Despesa",   "Devedora"),
    ("5.1.10","Desp. Pre-operacional","Resultado Despesa",  "Devedora"),
]
cursor.executemany(
    "INSERT OR IGNORE INTO plano_contas VALUES (?,?,?,?)", plano
)
conn.commit()
print(f"✅ Plano de contas: {len(plano)} contas inseridas.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. CONSULTAS DE VERIFICAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
print("\n📊 Receita total:")
cursor.execute("""
    SELECT COALESCE(SUM(valor), 0)
    FROM lancamentos
    WHERE conta_credito = 'Rec. Servicos'
""")
rec = cursor.fetchone()[0]
print(f"  R$ {rec:,.2f}")

print("\n📊 Top 5 despesas:")
cursor.execute("""
    SELECT conta_debito, SUM(valor) AS total
    FROM lancamentos
    WHERE conta_debito LIKE 'Desp.%'
    GROUP BY conta_debito
    ORDER BY total DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]:<30} R$ {row[1]:>10,.2f}")

conn.close()
print(f"\n✅ Script 02 concluído. Banco '{ARQUIVO_DB}' pronto.")
print("   Execute 03_gerar_dre.py para o próximo passo.")

"""
UTI dos nerds – Script 03: Gerar DRE Automaticamente
Disciplina: SISB090 – Informação Contábil para Gestão
"""

import sqlite3

ARQUIVO_DB = "utidosnerds.db"

def saldo_credito(conn, conta):
    r = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_credito=?",
        (conta,)
    )
    return r.fetchone()[0]

def saldo_debito(conn, conta):
    r = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?",
        (conta,)
    )
    return r.fetchone()[0]

def saldo_debito_mes(conn, conta, mes):
    r = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos "
        "WHERE conta_debito=? AND mes=?",
        (conta, mes)
    )
    return r.fetchone()[0]

def saldo_credito_mes(conn, conta, mes):
    r = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos "
        "WHERE conta_credito=? AND mes=?",
        (conta, mes)
    )
    return r.fetchone()[0]

# ─────────────────────────────────────────────────────────────────────────────
conn = sqlite3.connect(ARQUIVO_DB)

contas_despesa = [
    "Desp. Salarios", "Desp. FGTS", "Desp. INSS Patronal",
    "Desp. Pro-labore", "Desp. Aluguel", "Desp. Telecom",
    "Desp. Mat. Escritorio", "Desp. Depreciacao", "Desp. Pre-operacional"
]

meses = ["Mai", "Jun", "Jul"]
nomes_meses = {"Mai": "Maio/2026", "Jun": "Junho/2026", "Jul": "Julho/2026"}

print("=" * 65)
print("  DEMONSTRAÇÃO DO RESULTADO – UTI dos Nerds")
print("=" * 65)

resultados = {}

for mes in meses:
    rec_bruta = saldo_credito_mes(conn, "Rec. Servicos", mes)
    das       = saldo_debito_mes(conn, "Desp. Tributos", mes)
    rec_liq   = rec_bruta - das

    desp = {c: saldo_debito_mes(conn, c, mes) for c in contas_despesa}
    total_desp = sum(desp.values())
    lucro_liq  = rec_liq - total_desp

    # Análise Vertical
    av = lambda v: f"{(v/rec_bruta*100):.1f}%" if rec_bruta else "–"

    resultados[mes] = {
        "rec_bruta": rec_bruta, "das": das, "rec_liq": rec_liq,
        "desp": desp, "total_desp": total_desp, "lucro_liq": lucro_liq
    }

# Imprimir DRE comparativa
larg = 28
sep  = "─" * (larg + 42)

header = f"{'Descrição':<{larg}}" + "".join(
    f"{nomes_meses[m]:>13}" for m in meses)
print(f"\n{header}")
print(sep)

def linha(descricao, chave, bold=False):
    vals = [resultados[m][chave] for m in meses]
    prefix = "  " if not bold else ""
    txt = f"{prefix}{descricao:<{larg-len(prefix)}}"
    nums = "".join(f"  R${v:>10,.2f}" for v in vals)
    if bold:
        print(f"\033[1m{txt}{nums}\033[0m")
    else:
        print(f"{txt}{nums}")

linha("1. Receita Bruta de Serviços", "rec_bruta", bold=True)
print(f"  {'(–) DAS – Simples Nacional':<{larg-2}}"
      + "".join(f"  R${-resultados[m]['das']:>10,.2f}" for m in meses))
print(sep)
linha("2. RECEITA LÍQUIDA", "rec_liq", bold=True)
print(f"\n  {'(–) Desp. Operacionais (total)':<{larg-2}}"
      + "".join(f"  R${-resultados[m]['total_desp']:>10,.2f}" for m in meses))
print(sep)
linha("= LUCRO LÍQUIDO", "lucro_liq", bold=True)

print(f"\n{'Margem Líquida':<{larg}}"
      + "".join(
    f"  {'–':>13}" if resultados[m]['rec_bruta']==0
    else f"  {resultados[m]['lucro_liq']/resultados[m]['rec_bruta']*100:>12.1f}%"
    for m in meses))

conn.close()
print(f"\n✅ Script 03 concluído. Execute 04_gerar_bp.py para o próximo passo.")

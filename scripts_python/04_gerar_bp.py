"""
UTI dos Nerds – Script 04: Gerar Balanço Patrimonial
Disciplina: SISB090 – Informação Contábil para Gestão
"""

import sqlite3

ARQUIVO_DB = "utidosnerds.db"

def saldo_final(conn, conta):
    """Saldo final = Débitos acumulados – Créditos acumulados."""
    d = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?",
        (conta,)
    ).fetchone()[0]
    c = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_credito=?",
        (conta,)
    ).fetchone()[0]
    return d - c

conn = sqlite3.connect(ARQUIVO_DB)
larg = 32

print("=" * 65)
print("  BALANÇO PATRIMONIAL – UTI dos nerds")
print("  (Acumulado até Julho/2026)")
print("=" * 65)

# ── ATIVO ─────────────────────────────────────────────────────────────────
print("\n  ┌─ ATIVO " + "─" * 54)

ativo_circ = {
    "Caixa":    max(0, saldo_final(conn, "Caixa")),
    "Banco":    max(0, saldo_final(conn, "Banco")),
    "Clientes": max(0, saldo_final(conn, "Clientes")),
}
print(f"\n  {'ATIVO CIRCULANTE':}")
for conta, saldo in ativo_circ.items():
    print(f"    {conta:<28}  R$ {saldo:>12,.2f}")
total_ac = sum(ativo_circ.values())
print(f"  {'  TOTAL ATIVO CIRCULANTE':<32}  R$ {total_ac:>12,.2f}  ◄")

equip  = max(0, saldo_final(conn, "Equipamentos de TI"))
moveis = max(0, saldo_final(conn, "Moveis e Utensilios"))
dep    = min(0, saldo_final(conn, "Depreciacao Acumulada"))
total_anc = equip + moveis + dep

print(f"\n  {'ATIVO NÃO CIRCULANTE':}")
print(f"    {'Equipamentos de TI':<28}  R$ {equip:>12,.2f}")
print(f"    {'Móveis e Utensílios':<28}  R$ {moveis:>12,.2f}")
print(f"    {'(–) Depreciação Acumulada':<28}  R$ {dep:>12,.2f}")
print(f"  {'  TOTAL ATIVO NÃO CIRCULANTE':<32}  R$ {total_anc:>12,.2f}  ◄")

total_ativo = total_ac + total_anc
print(f"\n  {'  ══ TOTAL GERAL DO ATIVO':<32}  R$ {total_ativo:>12,.2f}  ══")

# ── PASSIVO ───────────────────────────────────────────────────────────────
print("\n  ┌─ PASSIVO + PATRIMÔNIO LÍQUIDO " + "─" * 30)

pass_circ = {
    "DAS a Recolher":  max(0, -saldo_final(conn, "DAS a Recolher")),
    "FGTS a Recolher": max(0, -saldo_final(conn, "FGTS a Recolher")),
    "INSS a Recolher": max(0, -saldo_final(conn, "INSS a Recolher")),
}
print(f"\n  {'PASSIVO CIRCULANTE':}")
for conta, saldo in pass_circ.items():
    print(f"    {conta:<28}  R$ {saldo:>12,.2f}")
total_pc = sum(pass_circ.values())
print(f"  {'  TOTAL PASSIVO CIRCULANTE':<32}  R$ {total_pc:>12,.2f}  ◄")

cap_social  = max(0, -saldo_final(conn, "Capital Social"))
lucros_acum = max(0, -saldo_final(conn, "Lucros Acumulados"))
print(f"\n  {'PATRIMÔNIO LÍQUIDO':}")
print(f"    {'Capital Social':<28}  R$ {cap_social:>12,.2f}")
print(f"    {'Lucros Acumulados':<28}  R$ {lucros_acum:>12,.2f}")
total_pl = cap_social + lucros_acum
print(f"  {'  TOTAL PATRIMÔNIO LÍQUIDO':<32}  R$ {total_pl:>12,.2f}  ◄")

total_pp = total_pc + total_pl
print(f"\n  {'  ══ TOTAL PASSIVO + PL':<32}  R$ {total_pp:>12,.2f}  ══")

# ── VERIFICAÇÃO ───────────────────────────────────────────────────────────
print(f"\n  {'─' * 62}")
dif = total_ativo - total_pp
ok = "✅ EQUILIBRADO" if abs(dif) < 0.01 else f"⚠  DIFERENÇA: R$ {dif:,.2f}"
print(f"  Verificação (Ativo – Passivo+PL): {ok}")

conn.close()
print(f"\n✅ Script 04 concluído. Execute 05_calcular_indices.py.")

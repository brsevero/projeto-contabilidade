"""
UTI dos Nerds – Script 05: Calcular Índices Financeiros
Disciplina: SISB090 – Informação Contábil para Gestão
"""

import sqlite3

ARQUIVO_DB = "utidosnerds.db"

def q(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0] or 0

conn = sqlite3.connect(ARQUIVO_DB)

def get_bp_dre(conn):
    """Retorna dicionário com dados do BP e DRE."""
    # DRE
    rec_b = q(conn, "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_credito='Rec. Servicos'")
    das   = q(conn, "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito='Desp. Tributos'")
    rec_l = rec_b - das

    desp_contas = [
        "Desp. Salarios","Desp. FGTS","Desp. INSS Patronal",
        "Desp. Pro-labore","Desp. Aluguel","Desp. Telecom",
        "Desp. Mat. Escritorio","Desp. Depreciacao","Desp. Pre-operacional"
    ]
    desp = sum(q(conn, "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?", (c,))
               for c in desp_contas)
    ll = rec_l - desp

    def saldo(conta):
        d = q(conn, "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?", (conta,))
        c_ = q(conn, "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_credito=?", (conta,))
        return d - c_

    # BP
    banco   = max(0, saldo("Banco"))
    caixa   = max(0, saldo("Caixa"))
    clientes= max(0, saldo("Clientes"))
    ac      = banco + caixa + clientes

    equip   = max(0, saldo("Equipamentos de TI"))
    moveis  = max(0, saldo("Moveis e Utensilios"))
    dep     = min(0, saldo("Depreciacao Acumulada"))
    anc     = equip + moveis + dep
    at      = ac + anc

    das_rec = max(0, -saldo("DAS a Recolher"))
    fgts_r  = max(0, -saldo("FGTS a Recolher"))
    inss_r  = max(0, -saldo("INSS a Recolher"))
    pc      = das_rec + fgts_r + inss_r

    cap_s   = max(0, -saldo("Capital Social"))
    luc_ac  = max(0, -saldo("Lucros Acumulados"))
    pl      = cap_s + luc_ac
    pt      = pc

    return dict(
        rec_b=rec_b, rec_l=rec_l, ll=ll,
        ac=ac, anc=anc, at=at,
        pc=pc, pl=pl, pt=pt,
        banco=banco, clientes=clientes
    )

bp = get_bp_dre(conn)

def safe_div(a, b):
    return a / b if b != 0 else 0

indices = {
    "LIQUIDEZ": [
        ("Liquidez Corrente",    safe_div(bp['ac'], bp['pc']),          "> 1,5",    ""),
        ("Liquidez Imediata",    safe_div(bp['banco'], bp['pc']),        "> 0,5",    ""),
    ],
    "RENTABILIDADE": [
        ("Margem Líquida",       safe_div(bp['ll'], bp['rec_b']) * 100,  "> 10%",   "%"),
        ("ROE",                  safe_div(bp['ll'], bp['pl'])   * 100,   "> 12%",   "%"),
        ("ROA",                  safe_div(bp['ll'], bp['at'])   * 100,   "> 8%",    "%"),
    ],
    "ESTRUTURA DE CAPITAL": [
        ("Endividamento Geral",  safe_div(bp['pt'], bp['at'])  * 100,   "< 50%",   "%"),
        ("Giro do Ativo",        safe_div(bp['rec_l'], bp['at']),         "> 0,5",   ""),
    ],
    "ATIVIDADE": [
        ("PMRV (dias)",          safe_div(bp['clientes'], bp['rec_b']) * 30, "< 30d", " dias"),
    ],
}

print("=" * 65)
print("  ANÁLISE DE ÍNDICES FINANCEIROS – UTI dos Nerds (Acumulado)")
print("=" * 65)

for grupo, lista in indices.items():
    print(f"\n  ◆ {grupo}")
    print(f"  {'Índice':<30} {'Valor':>12}  {'Referência':>10}  {'Status':>8}")
    print("  " + "─" * 60)
    for nome, valor, ref, unid in lista:
        if unid == "%":
            v_str = f"{valor:.1f}%"
        elif "dias" in unid:
            v_str = f"{valor:.1f} dias"
        else:
            v_str = f"{valor:.2f}"
        print(f"  {nome:<30} {v_str:>12}  {ref:>10}")

conn.close()
print(f"\n✅ Script 05 concluído. Execute 06_graficos.py para visualizações.")

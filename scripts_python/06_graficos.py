"""
UTI dos Nerds – Script 06: Gerar Gráficos com Matplotlib
Disciplina: SISB090 – Informação Contábil para Gestão
"""

import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

ARQUIVO_DB = "utidosnerds.db"
conn = sqlite3.connect(ARQUIVO_DB)

# ─── Coletar dados por mês ────────────────────────────────────────────────
import pandas as pd

query = """
    SELECT
        mes,
        SUM(CASE WHEN conta_credito = 'Rec. Servicos' THEN valor ELSE 0 END) AS receita,
        SUM(CASE WHEN conta_debito  = 'Desp. Tributos' THEN valor ELSE 0 END) AS das,
        SUM(CASE WHEN conta_debito  LIKE 'Desp.%'
                  AND conta_debito <> 'Desp. Tributos' THEN valor ELSE 0 END) AS despesas
    FROM lancamentos
    WHERE mes IN ('Mai','Jun','Jul')
    GROUP BY mes
    ORDER BY CASE mes WHEN 'Mai' THEN 1 WHEN 'Jun' THEN 2 WHEN 'Jul' THEN 3 END
"""
df = pd.read_sql_query(query, conn)
conn.close()

df["receita_liq"] = df["receita"] - df["das"]
df["lucro"]       = df["receita_liq"] - df["despesas"]
df["margem"]      = (df["lucro"] / df["receita"] * 100).round(1)
df["mes_nome"]    = ["Maio/2026", "Junho/2026", "Julho/2026"]

# ─── Cores NexusTech ─────────────────────────────────────────────────────
AZUL  = "#1F3864"
VERDE = "#22783C"
VERD2 = "#A8D08D"
VERM  = "#B41E1E"
LARANJ= "#C65911"

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("UTI dos Nerds – Dashboard Financeiro (Mai–Jul/2026)",
             fontsize=13, fontweight='bold', color=AZUL, y=0.98)

meses = df["mes_nome"].tolist()
x = range(len(meses))
w = 0.35

# ── Gráfico 1: Receita × Lucro ────────────────────────────────────────────
ax1 = axes[0, 0]
b1 = ax1.bar([i - w/2 for i in x], df["receita"], width=w, color=AZUL, label="Receita Bruta")
b2 = ax1.bar([i + w/2 for i in x], df["lucro"],   width=w, color=VERDE, label="Lucro Líquido")
ax1.set_title("Receita Bruta vs. Lucro Líquido", fontweight='bold')
ax1.set_xticks(x); ax1.set_xticklabels(meses, rotation=15)
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"R${v/1000:.0f}k"))
ax1.legend(fontsize=8); ax1.grid(axis='y', alpha=0.3)
for bar in [*b1, *b2]:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, h + 200,
             f"R${h:,.0f}", ha='center', va='bottom', fontsize=7)

# ── Gráfico 2: Margem Líquida ─────────────────────────────────────────────
ax2 = axes[0, 1]
ax2.plot(meses, df["margem"], 'o-', color=VERM, linewidth=2.5, markersize=8)
ax2.fill_between(meses, df["margem"], alpha=0.15, color=VERM)
ax2.set_title("Margem Líquida (%)", fontweight='bold')
ax2.set_ylim(0, 70)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.grid(axis='y', alpha=0.3)
for i, (mes, mg) in enumerate(zip(meses, df["margem"])):
    ax2.annotate(f"{mg:.1f}%", (mes, mg), textcoords="offset points",
                 xytext=(0, 8), ha='center', fontweight='bold', color=VERM)

# ── Gráfico 3: Composição das Despesas ────────────────────────────────────
ax3 = axes[1, 0]
# Criar dados empilhados para Julho
try:
    conn2 = sqlite3.connect(ARQUIVO_DB)
    desp_labels = [
        ("Pró-labore","Desp. Pro-labore"),
        ("Salários","Desp. Salarios"),
        ("Encargos","Desp. INSS Patronal"),
        ("Aluguel","Desp. Aluguel"),
        ("Outros","Desp. Telecom"),
    ]
    vals = []
    for lbl, conta in desp_labels:
        r = conn2.execute(
            "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?",
            (conta,)
        ).fetchone()[0]
        vals.append(r)
    conn2.close()
    cores_pie = [AZUL, VERDE, LARANJ, VERM, "#8EA9C1"]
    wedges, texts, autotexts = ax3.pie(
        vals, labels=[l for l,_ in desp_labels],
        autopct='%1.0f%%', colors=cores_pie, startangle=90,
        textprops={'fontsize': 8}
    )
    ax3.set_title("Composição das Despesas (Total)", fontweight='bold')
except Exception as e:
    ax3.text(0.5, 0.5, "Sem dados", ha='center', va='center')

# ── Gráfico 4: Evolução do Patrimônio Líquido ─────────────────────────────
ax4 = axes[1, 1]
pl_vals = [57797, 61819, 59944]   # valores de referência
ax4.bar(meses, pl_vals, color=[AZUL, AZUL, AZUL], alpha=0.8)
ax4.plot(meses, pl_vals, 'D-', color=VERDE, linewidth=2, markersize=7)
ax4.set_title("Evolução do Patrimônio Líquido (R$)", fontweight='bold')
ax4.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"R${v/1000:.0f}k"))
ax4.set_ylim(50000, 70000)
ax4.grid(axis='y', alpha=0.3)
for mes, pl in zip(meses, pl_vals):
    ax4.text(mes, pl + 400, f"R${pl:,.0f}", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig("graficos_nexustech.pdf", dpi=150, bbox_inches='tight')
plt.savefig("graficos_nexustech.png", dpi=150, bbox_inches='tight')
print("✅ Gráficos salvos: 'graficos_nexustech.pdf' e 'graficos_nexustech.png'")
plt.show()

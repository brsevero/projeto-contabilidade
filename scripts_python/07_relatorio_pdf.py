"""
UTI dos Nerds – Script 07: Gerar Relatório Financeiro em PDF
Disciplina: SISB090 – Informação Contábil para Gestão
Requer: pip install fpdf2
"""

import sqlite3
from fpdf import FPDF
from datetime import date

ARQUIVO_DB = "utidosnerds.db"

# ─── Coletar dados ────────────────────────────────────────────────────────
conn = sqlite3.connect(ARQUIVO_DB)

def q(sql, p=()):
    return conn.execute(sql, p).fetchone()[0] or 0

def saldo(conta):
    d = q("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?", (conta,))
    c = q("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_credito=?", (conta,))
    return d - c

rec_b  = q("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_credito='Rec. Servicos'")
das    = q("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito='Desp. Tributos'")
rec_l  = rec_b - das
desp_contas = ["Desp. Salarios","Desp. FGTS","Desp. INSS Patronal",
               "Desp. Pro-labore","Desp. Aluguel","Desp. Telecom",
               "Desp. Mat. Escritorio","Desp. Depreciacao"]
total_desp = sum(q("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?", (c,))
                 for c in desp_contas)
ll = rec_l - total_desp
banco   = max(0, saldo("Banco"))
clientes= max(0, saldo("Clientes"))
equip   = max(0, saldo("Equipamentos de TI"))
dep     = abs(min(0, saldo("Depreciacao Acumulada")))
ac      = banco + clientes
anc     = equip - dep
at      = ac + anc
das_r   = max(0, -saldo("DAS a Recolher"))
fgts_r  = max(0, -saldo("FGTS a Recolher"))
inss_r  = max(0, -saldo("INSS a Recolher"))
pc      = das_r + fgts_r + inss_r
cap_s   = max(0, -saldo("Capital Social"))
luc_ac  = max(0, -saldo("Lucros Acumulados"))
pl      = cap_s + luc_ac
conn.close()

def pct(v, base):
    return f"{v/base*100:.1f}%" if base else "–"

# ─── Criar PDF ────────────────────────────────────────────────────────────
class Relatorio(FPDF):
    def header(self):
        self.set_fill_color(31, 56, 100)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 10,
                  "NexusTech Penedo Soluções Digitais Ltda. – Relatório Financeiro",
                  align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Página {self.page_no()} | Gerado em {date.today().strftime('%d/%m/%Y')}", align="C")

    def secao(self, titulo, cor=(31, 56, 100)):
        self.set_fill_color(*cor)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, f"  {titulo}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def linha_dre(self, desc, valor, bold=False, negrito=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 9)
        self.cell(130, 6, f"  {desc}")
        sinal = "" if valor >= 0 else ""
        self.cell(0, 6, f"R$ {valor:>12,.2f}", align="R",
                  new_x="LMARGIN", new_y="NEXT")

    def linha_bp(self, desc, valor, indent=0, bold=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 9)
        prefixo = "  " * indent
        self.cell(100, 5, f"{prefixo}{desc}")
        self.cell(0, 5, f"R$ {valor:>12,.2f}", align="R",
                  new_x="LMARGIN", new_y="NEXT")

pdf = Relatorio(orientation='P', format='A4')
pdf.set_margins(15, 15, 15)
pdf.add_page()

# ── Identificação ──────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 8, "UTI dos Nerds, venda e manutenção de celulares LTDA.", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, "CNPJ: 12.345.678/0001-90 | Penedo/AL",
         align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, f"Relatório Financeiro – Período: Maio a Julho/2026 | Emissão: {date.today().strftime('%d/%m/%Y')}",
         align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

# ── DRE ───────────────────────────────────────────────────────────────────
pdf.secao("DEMONSTRAÇÃO DO RESULTADO (DRE) – Acumulado Mai–Jul/2026")
pdf.linha_dre("Receita Bruta de Serviços", rec_b)
pdf.linha_dre("(–) DAS – Simples Nacional", -das)
pdf.set_draw_color(70, 110, 180)
pdf.cell(0, 0.5, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.linha_dre("= RECEITA LÍQUIDA", rec_l, bold=True)
for conta in desp_contas:
    v = conn2 = sqlite3.connect(ARQUIVO_DB)
    v_val = conn2.execute(
        "SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE conta_debito=?",
        (conta,)
    ).fetchone()[0]; conn2.close()
    if v_val > 0:
        pdf.linha_dre(f"  (–) {conta}", -v_val)
pdf.linha_dre("(–) Total Despesas Operacionais", -total_desp, bold=True)
pdf.cell(0, 0.5, fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 10)
pdf.set_fill_color(34, 120, 60); pdf.set_text_color(255,255,255)
pdf.cell(130, 7, "  LUCRO LÍQUIDO DO EXERCÍCIO", fill=True)
pdf.cell(0, 7, f"R$ {ll:>12,.2f}", align="R", fill=True,
         new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0,0,0)

pdf.ln(3)
pdf.set_font("Helvetica", "", 9)
pdf.cell(0, 5, f"  Margem Líquida: {pct(ll, rec_b)}  |  "
               f"Margem Operacional: {pct(ll, rec_l)}",
         new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

# ── BP ────────────────────────────────────────────────────────────────────
pdf.secao("BALANÇO PATRIMONIAL (Posição Acumulada)")
pdf.set_font("Helvetica", "B", 9)
pdf.cell(90, 6, "  ATIVO"); pdf.cell(0, 6, "  PASSIVO + PL",
                                      new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 9)
rows = [
    (f"  Banco: R${banco:,.2f}",       f"  DAS a Recolher: R${das_r:,.2f}"),
    (f"  Clientes: R${clientes:,.2f}", f"  FGTS a Rec.: R${fgts_r:,.2f}"),
    (f"  Total AC: R${ac:,.2f}",       f"  INSS a Rec.: R${inss_r:,.2f}"),
    (f"  Equip.TI: R${equip:,.2f}",    f"  Total PC: R${pc:,.2f}"),
    (f"  (-) Dep. Acum.: R${-dep:,.2f}",f"  Capital Social: R${cap_s:,.2f}"),
    (f"  Total ANC: R${anc:,.2f}",     f"  Lucros Acum.: R${luc_ac:,.2f}"),
    (f"  TOTAL ATIVO: R${at:,.2f}",    f"  TOTAL PL: R${pl:,.2f}"),
]
for left, right in rows:
    bold = "TOTAL" in left
    style = "B" if bold else ""
    pdf.set_font("Helvetica", style, 9)
    pdf.cell(90, 5, left); pdf.cell(0, 5, right,
                                     new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# ── Índices ───────────────────────────────────────────────────────────────
pdf.secao("INDICADORES FINANCEIROS PRINCIPAIS", cor=(70, 110, 180))
safe_div = lambda a, b: a/b if b else 0
indices = [
    ("Liquidez Corrente",   f"{safe_div(ac, pc):.2f}",          "> 1,5"),
    ("Margem Líquida",      f"{safe_div(ll, rec_b)*100:.1f}%",  "> 10%"),
    ("ROE",                 f"{safe_div(ll, pl)*100:.1f}%",     "> 12%"),
    ("Endividamento Geral", f"{safe_div(pc, at)*100:.1f}%",     "< 50%"),
    ("Giro do Ativo",       f"{safe_div(rec_l, at):.2f}",       "> 0,5"),
]
pdf.set_font("Helvetica", "B", 9)
pdf.cell(80, 6, "  Índice"); pdf.cell(40, 6, "Valor", align="C")
pdf.cell(0, 6, "Referência", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 9)
for nome, valor, ref in indices:
    pdf.cell(80, 5, f"  {nome}")
    pdf.cell(40, 5, valor, align="C")
    pdf.cell(0, 5, ref, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

# ── Análise ───────────────────────────────────────────────────────────────
pdf.secao("ANÁLISE GERENCIAL", cor=(34, 120, 60))
pdf.set_font("Helvetica", "", 9)
analise = (
    "A NexusTech apresentou crescimento consistente de receita ao longo do período analisado, "
    f"com receita bruta acumulada de R$ {rec_b:,.2f} e margem líquida de {pct(ll, rec_b)}. "
    "O baixo endividamento e a liquidez corrente elevada indicam solidez financeira. "
    "Recomenda-se expandir a carteira de clientes B2B e avaliar reinvestimento em ativos produtivos."
)
pdf.multi_cell(0, 5, f"  {analise}")

pdf.ln(3)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(100, 100, 100)
pdf.multi_cell(0, 5, "  * Relatório gerado automaticamente a partir do banco de dados "
                      "nexustech.db via Python (SISB090 – UFAL Penedo).")

pdf.output("relatorio_nexustech.pdf")
print("✅ Relatório salvo: 'relatorio_nexustech.pdf'")
print("\n🎉 Todos os scripts concluídos! Pasta nexustech_projeto pronta para entrega.")

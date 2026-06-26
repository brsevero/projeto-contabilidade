"""
UTI dos Nerds – Script 01: Importar e Validar Planilha de Lançamentos
Disciplina: SISB090 – Informação Contábil para Gestão
UFAL – Unidade Penedo | Prof. Dr. Valber Gregory
Prazo de entrega: 22/06/2026
"""

import pandas as pd
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
ARQUIVO_PLANILHA = "UTI_dos_nerds_Atividades.xlsx"  # deve estar na mesma pasta
ABA_LANCAMENTOS  = "LANCAMENTOS"

# ─────────────────────────────────────────────────────────────────────────────
# 1. LER A PLANILHA
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("  UTI_dos_nerds – Importação de Lançamentos Contábeis")
print("=" * 60)

if not os.path.exists(ARQUIVO_PLANILHA):
    raise FileNotFoundError(
        f"Arquivo '{ARQUIVO_PLANILHA}' não encontrado.\n"
        f"Coloque a planilha na mesma pasta que este script."
    )

# Ler apenas as colunas necessárias (ignorar primeiras 3 colunas auxiliares)
df = pd.read_excel(
    ARQUIVO_PLANILHA,
    sheet_name=ABA_LANCAMENTOS,
    header=2,          # linha 3 é o cabeçalho (índice 2)
    usecols="B:I",     # colunas C a J
    dtype=str          # ler tudo como texto primeiro
)

# Renomear colunas para nomes sem acentos
df.columns = ["mes", "n_lancamento", "data", "doc",
              "descricao", "conta_debito", "conta_credito", "valor"]

print(f"\n📊 Linhas lidas: {len(df)}")
print(f"📋 Colunas: {list(df.columns)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. LIMPEZA E PADRONIZAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

# Remover linhas que sejam separadores de mês ou completamente vazias
df = df[df["n_lancamento"].notna()]           # remove linhas sem número
df = df[~df["conta_debito"].isna()]           # remove sem conta débito
df = df.reset_index(drop=True)

# Padronizar nomes de contas (remover espaços extras)
df["conta_debito"]  = df["conta_debito"].str.strip()
df["conta_credito"] = df["conta_credito"].str.strip()
df["descricao"]     = df["descricao"].str.strip()

# Converter data
df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")

# Converter valor para numérico
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

print(f"\n✅ Após limpeza: {len(df)} lançamentos válidos")
# ─────────────────────────────────────────────────────────────────────────────
# 3. VALIDAÇÕES
# ─────────────────────────────────────────────────────────────────────────────
print("\n🔍 Validações:")

# Verificar datas inválidas
datas_invalidas = df[df["data"].isna()]
if len(datas_invalidas) > 0:
    print(f"  ⚠  Datas inválidas: {len(datas_invalidas)} linhas")
    print(datas_invalidas[["n_lancamento", "data"]].to_string())
else:
    print("  ✓  Todas as datas são válidas.")

# Verificar valores inválidos
valores_invalidos = df[df["valor"].isna() | (df["valor"] <= 0)]
if len(valores_invalidos) > 0:
    print(f"  ⚠  Valores inválidos: {len(valores_invalidos)} linhas")
else:
    print("  ✓  Todos os valores são positivos.")

# Verificar contas em branco
contas_vazias = df[df["conta_debito"].isna() | df["conta_credito"].isna()]
if len(contas_vazias) > 0:
    print(f"  ⚠  Contas em branco: {len(contas_vazias)} linhas")
else:
    print("  ✓  Todas as contas estão preenchidas.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. RELATÓRIO FINAL
# ─────────────────────────────────────────────────────────────────────────────
print("\n📈 Resumo por mês:")
resumo = df.groupby("mes")["valor"].agg(["count", "sum"]).reset_index()
resumo.columns = ["Mês", "Qtd. Lançamentos", "Total (R$)"]
print(resumo.to_string(index=False))

print(f"\n💰 Total geral lançado: R$ {df['valor'].sum():,.2f}")
print(f"📅 Período: {df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}")

print("\n✅ Script 01 concluído. Execute 02_criar_db.py para o próximo passo.")

# Salvar df para uso pelos scripts seguintes
df.to_csv("lancamentos_limpos.csv", index=False, encoding="utf-8-sig",
          date_format="%Y-%m-%d")
print("💾 Arquivo 'lancamentos_limpos.csv' salvo.")

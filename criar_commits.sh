#!/usr/bin/env bash
# SalesInsight PY – cria os 5 commits (Linux / GitHub Codespaces / Git Bash)
# Uso: cd /workspaces/salesinsight-py && bash scripts/criar_commits.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f salesinsight.py ]]; then
  echo "ERRO: salesinsight.py nao existe em $ROOT"
  ls -la
  exit 1
fi

if ! command -v git &>/dev/null; then
  echo "ERRO: git nao instalado."
  exit 1
fi

cp salesinsight.py _salesinsight_full.py

if [[ "${RECRIAR_HISTORICO:-0}" == "1" ]]; then
  echo "Recriando repositorio do zero (RECRIAR_HISTORICO=1)..."
  rm -rf .git
fi

if [[ ! -d .git ]]; then
  git init
  git checkout -B main 2>/dev/null || git branch -M main
fi

# --- Commit 1 ---
cat > salesinsight.py << 'EOF'
"""SalesInsight PY – Pipeline de Análise e Visualização de Dados de Vendas."""
from __future__ import annotations
EOF

git add salesinsight.py
[[ -f .gitignore ]] && git add .gitignore
[[ -f requirements.txt ]] && git add requirements.txt
git commit -m "feat: cria estrutura inicial do projeto e arquivo salesinsight.py"

# --- Commit 2 (linhas 1-100) ---
head -n 100 _salesinsight_full.py > salesinsight.py
git add salesinsight.py
git commit -m "feat: adiciona função de geração e leitura do dataset CSV"

# --- Commit 3 (linhas 1-173) ---
head -n 173 _salesinsight_full.py > salesinsight.py
git add salesinsight.py
git commit -m "feat: implementa limpeza de dados e tratamento de nulos"

# --- Commit 4 (linhas 1-332) ---
head -n 332 _salesinsight_full.py > salesinsight.py
git add salesinsight.py
git commit -m "feat: adiciona transformações de colunas e extração de datas"

# --- Commit 5 (arquivo completo + docs) ---
cp _salesinsight_full.py salesinsight.py
rm -f _salesinsight_full.py

git add salesinsight.py
[[ -f README.md ]] && git add README.md
[[ -f planejamento/tarefas-kanban.md ]] && git add planejamento/tarefas-kanban.md
[[ -f vendas.csv ]] && git add vendas.csv
[[ -f scripts/criar_commits.sh ]] && git add scripts/criar_commits.sh
[[ -f .gitattributes ]] && git add .gitattributes
[[ -f .gitignore ]] && git add .gitignore
[[ -f requirements.txt ]] && git add requirements.txt
git commit -m "feat: adiciona visualizações, classes com herança e exportação CSV/JSON"

echo ""
echo "Commits criados:"
git log --oneline -5

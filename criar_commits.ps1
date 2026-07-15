# SalesInsight PY – cria os 5 commits do mini-projeto (individual)
# Execute na pasta raiz do projeto:  .\scripts\criar_commits.ps1

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

# Localiza git.exe
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    $candidatos = @(
        "${env:ProgramFiles}\Git\bin\git.exe",
        "${env:ProgramFiles(x86)}\Git\bin\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
    )
    foreach ($c in $candidatos) {
        if (Test-Path $c) { $git = $c; break }
    }
}
if (-not $git) {
    Write-Host "ERRO: Git nao encontrado. Instale em https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}
if ($git -is [System.Management.Automation.ApplicationInfo]) {
    $gitExe = $git.Source
} else {
    $gitExe = $git
}

function Invoke-Git {
    param([string[]]$Args)
    & $gitExe @Args
    if ($LASTEXITCODE -ne 0) { throw "git falhou: git $($Args -join ' ')" }
}

$pyFile = Join-Path $root "salesinsight.py"
if (-not (Test-Path $pyFile)) {
    Write-Host "ERRO: salesinsight.py nao encontrado em $root" -ForegroundColor Red
    exit 1
}

Copy-Item $pyFile "_salesinsight_full.py" -Force

# Remove repo anterior se quiser recomecar (descomente a linha abaixo)
# if (Test-Path .git) { Remove-Item -Recurse -Force .git }

if (-not (Test-Path .git)) {
    Invoke-Git init
    Invoke-Git config user.email "ludilais@gmail.com"
    Invoke-Git config user.name "Ludmila"
}

# --- Commit 1: estrutura ---
@"
"""SalesInsight PY – Pipeline de Análise e Visualização de Dados de Vendas."""
from __future__ import annotations
"@ | Set-Content -Encoding utf8NoBOM $pyFile

Invoke-Git add .gitignore requirements.txt salesinsight.py
Invoke-Git commit -m "feat: cria estrutura inicial do projeto e arquivo salesinsight.py"

# --- Commit 2: geracao e inspecao (ate linha 100) ---
(Get-Content "_salesinsight_full.py" -TotalCount 100) | Set-Content -Encoding utf8NoBOM $pyFile
Invoke-Git add salesinsight.py
Invoke-Git commit -m "feat: adiciona função de geração e leitura do dataset CSV"

# --- Commit 3: limpeza e regex (ate linha 173) ---
(Get-Content "_salesinsight_full.py" -TotalCount 173) | Set-Content -Encoding utf8NoBOM $pyFile
Invoke-Git add salesinsight.py
Invoke-Git commit -m "feat: implementa limpeza de dados e tratamento de nulos"

# --- Commit 4: transformacoes, metricas, numpy (ate linha 332) ---
(Get-Content "_salesinsight_full.py" -TotalCount 332) | Set-Content -Encoding utf8NoBOM $pyFile
Invoke-Git add salesinsight.py
Invoke-Git commit -m "feat: adiciona transformações de colunas e extração de datas"

# --- Commit 5: pipeline completo + documentacao ---
Copy-Item "_salesinsight_full.py" $pyFile -Force
Remove-Item "_salesinsight_full.py" -Force

Invoke-Git add salesinsight.py README.md planejamento/tarefas-kanban.md
if (Test-Path vendas.csv) { Invoke-Git add vendas.csv }
Invoke-Git commit -m "feat: adiciona visualizações, classes com herança e exportação CSV/JSON" -m "Inclui README, Kanban, main() e pipeline completo."

Write-Host ""
Write-Host "Commits criados com sucesso:" -ForegroundColor Green
Invoke-Git log --oneline -5
Write-Host ""
Write-Host "Proximo passo: crie o repositorio no GitHub e execute:" -ForegroundColor Cyan
Write-Host "  git branch develop"
Write-Host "  git branch feat/pipeline-dados"
Write-Host "  git branch docs/readme"
Write-Host "  git remote add origin https://github.com/SEU_USUARIO/salesinsight-py.git"
Write-Host "  git push -u origin main"

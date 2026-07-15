# Histórico dos 5 commits (projeto individual)

### GitHub Codespaces / Linux / Mac

Se aparecer erro `$'\r': command not found`, converta o script para Linux:

```bash
sed -i 's/\r$//' scripts/criar_commits.sh
```

Depois:

```bash
cd /workspaces/salesinsight-py
RECRIAR_HISTORICO=1 bash scripts/criar_commits.sh
```

### Windows (PowerShell)

```powershell
cd C:\Users\ludil\salesinsight-py
.\scripts\criar_commits.ps1
```

Antes de rodar, edite no script seu **e-mail** e **nome** (`git config`).

## Commits gerados

| # | Mensagem | Conteúdo principal |
|---|----------|-------------------|
| 1 | `feat: cria estrutura inicial do projeto e arquivo salesinsight.py` | `.gitignore`, `requirements.txt`, esqueleto do `.py` |
| 2 | `feat: adiciona função de geração e leitura do dataset CSV` | `gerar_dataset_vendas`, `inspecionar_dados` |
| 3 | `feat: implementa limpeza de dados e tratamento de nulos` | `limpar_dados`, regex, `processar_coluna` |
| 4 | `feat: adiciona transformações de colunas e extração de datas` | colunas derivadas, `groupby`, NumPy, segmentação |
| 5 | `feat: adiciona visualizações, classes com herança e exportação CSV/JSON` | gráficos, classes, `main()`, README, Kanban, `vendas.csv` |

## Branches sugeridas (após os commits)

```powershell
git branch develop
git branch feat/pipeline-dados
git branch docs/readme
```

## Publicar no GitHub

1. Crie o repositório **salesinsight-py** (público).
2. No terminal:

```powershell
git remote add origin https://github.com/SEU_USUARIO/salesinsight-py.git
git push -u origin main
git push origin develop feat/pipeline-dados docs/readme
```

## GitHub Desktop

1. **File → Add local repository** → pasta `salesinsight-py`
2. Se ainda não tiver commits, rode o script `criar_commits.ps1` antes.
3. **Publish repository** → marque **Public**.

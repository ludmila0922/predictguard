# GitFlow – PredictGuard

Execute estes comandos após instalar o Git e criar o repositório no GitHub.

## 1. Inicializar e criar branches

```bash
git init
git checkout -b develop
git checkout -b feat/eda
git checkout -b feat/data-prep
git checkout -b feat/feature-engineering
git checkout -b feat/modelagem
git checkout -b docs/readme
git checkout develop
```

## 2. Commits sugeridos (por branch)

### feat/eda
```bash
git checkout feat/eda
git add data/manutencao_preditiva.csv predictguard.ipynb
git commit -m "implementa fase 1 - analise exploratoria"
git checkout develop
git merge feat/eda
```

### feat/data-prep
```bash
git checkout feat/data-prep
git add predictguard.ipynb
git commit -m "implementa fase 2 - limpeza e tratamento"
git checkout develop
git merge feat/data-prep
```

### feat/feature-engineering
```bash
git checkout feat/feature-engineering
git add predictguard.ipynb
git commit -m "implementa fase 3 - feature potencia"
git checkout develop
git merge feat/feature-engineering
```

### feat/modelagem
```bash
git checkout feat/modelagem
git add predictguard.ipynb requirements.txt scripts/
git commit -m "implementa fases 4 a 7 - modelagem e avaliacao"
git checkout develop
git merge feat/modelagem
```

### docs/readme
```bash
git checkout docs/readme
git add README.md planejamento/
git commit -m "adiciona documentacao e kanban"
git checkout develop
git merge docs/readme
```

## 3. Publicar em main

```bash
git checkout -b main
git merge develop
git remote add origin https://github.com/ludmila0922/predictguard.git
git push -u origin main
git push origin develop
git push origin feat/eda feat/data-prep feat/feature-engineering feat/modelagem docs/readme
```

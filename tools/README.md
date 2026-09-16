# Enviar um projeto inteiro para o ChatGPT

`bundle_project.sh` pega numa pasta de projeto e escreve todo o codigo-fonte
em ficheiros `.md` prontos a anexar no ChatGPT — com a arvore de directorios
no cabecalho e cada ficheiro num bloco de codigo identificado pelo caminho.

## Uso rapido

```sh
./tools/bundle_project.sh ~/projetos/trfl-perfumes
```

Gera `./chatgpt-bundle/trfl-perfumes.md`. Se o projeto for grande, sai dividido
em `trfl-perfumes-parte-01.md`, `-parte-02.md`, etc. — cada parte diz ao modelo
quantas faltam, para ele esperar antes de analisar.

## Opcoes

| Opcao | Efeito |
|---|---|
| `-o, --out DIR` | pasta de saida (default `./chatgpt-bundle`) |
| `-n, --name NOME` | nome base do bundle (default: nome da pasta) |
| `-m, --max-bytes N` | bytes por parte (default `350000`; `0` = ficheiro unico) |
| `-f, --max-file-kb N` | salta ficheiros maiores que N KB (default `256`) |
| `-z, --zip` | cria tambem um `.zip` com os ficheiros originais |
| `--no-gitignore` | nao respeitar o `.gitignore` |
| `--include-all` | desligar a lista de exclusoes por omissao |

## O que fica de fora

Automaticamente, para o dump nao ficar cheio de lixo:

- **Dependencias e builds**: `node_modules/`, `vendor/`, `dist/`, `build/`,
  `target/`, `.next/`, `__pycache__/`, `venv/`, `Pods/`, ...
- **Binarios**: imagens, video, audio, PDFs, fontes, `.o`, `.a`, `.exe`,
  bases de dados. Ficheiros binarios com extensao invulgar sao detetados pelo
  conteudo.
- **Ruido**: lockfiles (`package-lock.json`, `yarn.lock`, ...), `*.min.js`,
  source maps, `*.log`.
- **Ficheiros grandes** (> 256 KB por omissao).

Numa pasta com git, o `.gitignore` e respeitado — ou seja, ficheiros como
`.env` que ja estejam ignorados nao entram no bundle. **Confirma na mesma o
ficheiro gerado antes de o enviar**: se tiveres chaves ou passwords commitadas,
elas vao no dump. Um `grep -iE 'api[_-]?key|secret|password|token' bundle.md`
antes do upload custa pouco.

## Alternativas

Se preferires nao correr o script:

1. **Zip** — `./tools/bundle_project.sh -z projeto/` e anexas o `.zip`.
   O ChatGPT consegue descompactar e ler ficheiro a ficheiro no modo de
   analise de dados. Bom para projetos grandes, mas o modelo tem de ir abrir
   cada ficheiro em vez de os ter todos a vista.

2. **Se o projeto ja estiver no GitHub** — o mais rapido de todos:
   - [gitingest.com](https://gitingest.com) — troca `github.com` por
     `gitingest.com` no URL do repo e recebes um dump de texto unico.
   - [uithub.com](https://uithub.com) — mesma ideia, troca `github.com` por
     `uithub.com`.
   - `npx repomix` — corre localmente e produz um ficheiro so.
   - O conector de GitHub do proprio ChatGPT, que le o repo diretamente.

3. **Copiar e colar** — so para projetos pequenos. Acima de uns milhares de
   linhas e mais fiavel anexar ficheiros.

## Notas sobre limites

O ChatGPT limita o numero de anexos por conversa e, em ficheiros muito
compridos, pesquisa por excertos em vez de ler tudo de uma vez. Por isso o
default divide em partes de ~350 KB em vez de despejar tudo num ficheiro
gigante. Se o projeto for mesmo grande, vale mais enviar so a parte relevante
(`./tools/bundle_project.sh projeto/src`) do que o repositorio todo.

## Requisitos

`bash`, `awk`, `grep`, `sed`, `find` — presentes em qualquer macOS ou Linux.
O `zip` so e preciso com a opcao `-z`. Nao precisa de Python nem de `tree`.

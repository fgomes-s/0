#!/usr/bin/env bash
#
# bundle_project.sh — empacota um projeto inteiro em ficheiros de texto
# prontos a enviar para o ChatGPT (ou qualquer outro LLM).
#
# Percorre a pasta do projeto, ignora binarios/dependencias/artefactos de build,
# e escreve todo o codigo-fonte em um ou mais ficheiros .md com a arvore de
# directorios no cabecalho. Cada parte cabe dentro dos limites de upload.
#
# Uso:   ./bundle_project.sh [OPCOES] [PASTA_DO_PROJETO]
# Ajuda: ./bundle_project.sh --help

set -euo pipefail

VERSION="1.0.0"

# ---------------------------------------------------------------- defaults ---
PROJECT_DIR="."
OUT_DIR=""
BUNDLE_NAME=""
MAX_PART_BYTES=350000      # ~350 KB por parte (0 = ficheiro unico, sem cortes)
MAX_FILE_KB=256            # ficheiros maiores que isto sao listados mas nao incluidos
USE_GITIGNORE=1
INCLUDE_ALL=0
MAKE_ZIP=0

# Pastas e ficheiros ignorados por omissao (dependencias, builds, binarios).
EXCLUDE_DIRS=(
	.git .hg .svn
	node_modules bower_components vendor
	dist build out target .next .nuxt .output
	__pycache__ .venv venv env .tox .mypy_cache .pytest_cache .ruff_cache
	.idea .vscode .DS_Store
	coverage .nyc_output
	.cache .parcel-cache .turbo .gradle
	Pods
)
EXCLUDE_GLOBS=(
	'*.o' '*.a' '*.so' '*.dylib' '*.dll' '*.exe' '*.class' '*.jar' '*.pyc' '*.pyo'
	'*.png' '*.jpg' '*.jpeg' '*.gif' '*.webp' '*.svg' '*.ico' '*.bmp' '*.tiff'
	'*.mp3' '*.mp4' '*.mov' '*.avi' '*.wav' '*.webm' '*.ogg'
	'*.pdf' '*.zip' '*.tar' '*.gz' '*.tgz' '*.bz2' '*.xz' '*.rar' '*.7z'
	'*.woff' '*.woff2' '*.ttf' '*.otf' '*.eot'
	'*.sqlite' '*.sqlite3' '*.db' '*.pdb' '*.bin' '*.dat'
	'*.min.js' '*.min.css' '*.map'
	'package-lock.json' 'yarn.lock' 'pnpm-lock.yaml' 'composer.lock' 'Gemfile.lock'
	'poetry.lock' 'Cargo.lock'
	'*.log'
)

# ------------------------------------------------------------------- ajuda ---
usage() {
	cat <<'USAGE'
bundle_project.sh — poe um projeto inteiro num ficheiro para o ChatGPT

USO
  ./bundle_project.sh [OPCOES] [PASTA_DO_PROJETO]

OPCOES
  -o, --out DIR          pasta de saida            (default: ./chatgpt-bundle)
  -n, --name NOME        nome base do bundle       (default: nome da pasta)
  -m, --max-bytes N      bytes por parte           (default: 350000; 0 = nao dividir)
  -f, --max-file-kb N    salta ficheiros maiores que N KB (default: 256)
  -z, --zip              cria tambem um .zip com os ficheiros originais
      --no-gitignore     nao usar o .gitignore (inclui ficheiros ignorados)
      --include-all      desliga a lista de exclusoes por omissao
  -v, --version          mostra a versao
  -h, --help             mostra esta ajuda

EXEMPLOS
  ./bundle_project.sh ~/projetos/trfl-perfumes
  ./bundle_project.sh -o ~/Desktop -n trfl ~/projetos/trfl-perfumes
  ./bundle_project.sh --max-bytes 0 .            # tudo num unico ficheiro
  ./bundle_project.sh -z ~/projetos/trfl-perfumes

DEPOIS
  Faz upload dos .md gerados no ChatGPT (anexo de ficheiro). Se forem varias
  partes, envia-as por ordem: a Parte 1 explica ao modelo que ha mais partes
  a seguir.
USAGE
}

# ---------------------------------------------------------------- argumentos ---
POSITIONAL=()
while [ $# -gt 0 ]; do
	case "$1" in
		-o|--out)         OUT_DIR="${2:?--out precisa de um valor}"; shift 2 ;;
		-n|--name)        BUNDLE_NAME="${2:?--name precisa de um valor}"; shift 2 ;;
		-m|--max-bytes)   MAX_PART_BYTES="${2:?--max-bytes precisa de um valor}"; shift 2 ;;
		-f|--max-file-kb) MAX_FILE_KB="${2:?--max-file-kb precisa de um valor}"; shift 2 ;;
		-z|--zip)         MAKE_ZIP=1; shift ;;
		--no-gitignore)   USE_GITIGNORE=0; shift ;;
		--include-all)    INCLUDE_ALL=1; shift ;;
		-v|--version)     echo "bundle_project.sh $VERSION"; exit 0 ;;
		-h|--help)        usage; exit 0 ;;
		--)               shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
		-*)               echo "erro: opcao desconhecida '$1' (ver --help)" >&2; exit 2 ;;
		*)                POSITIONAL+=("$1"); shift ;;
	esac
done
if [ ${#POSITIONAL[@]} -gt 1 ]; then
	echo "erro: indica apenas uma pasta de projeto" >&2
	exit 2
fi
[ ${#POSITIONAL[@]} -eq 1 ] && PROJECT_DIR="${POSITIONAL[0]}"

case "$MAX_PART_BYTES" in ''|*[!0-9]*) echo "erro: --max-bytes tem de ser um numero" >&2; exit 2 ;; esac
case "$MAX_FILE_KB"    in ''|*[!0-9]*) echo "erro: --max-file-kb tem de ser um numero" >&2; exit 2 ;; esac

if [ ! -d "$PROJECT_DIR" ]; then
	echo "erro: '$PROJECT_DIR' nao e uma pasta" >&2
	exit 1
fi
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)"
[ -n "$BUNDLE_NAME" ] || BUNDLE_NAME="$(basename "$PROJECT_DIR")"
[ -n "$OUT_DIR" ] || OUT_DIR="$PWD/chatgpt-bundle"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd -P)"

# nome de ficheiro seguro (sem espacos nem barras)
SAFE_NAME="$(printf '%s' "$BUNDLE_NAME" | tr -cs 'A-Za-z0-9._-' '-' | sed 's/^-*//; s/-*$//')"
[ -n "$SAFE_NAME" ] || SAFE_NAME="projeto"

MAX_FILE_BYTES=$(( MAX_FILE_KB * 1024 ))
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/bundle.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

# ------------------------------------------------------------- recolha ---
# Numa pasta com git usamos `git ls-files` para respeitar o .gitignore;
# caso contrario percorremos com `find`.
list_candidates() {
	if [ "$USE_GITIGNORE" -eq 1 ] && git -C "$PROJECT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
		git -C "$PROJECT_DIR" ls-files -co --exclude-standard
	else
		local args=(find . -type f)
		local d
		for d in "${EXCLUDE_DIRS[@]}"; do
			args=("${args[@]}" -not -path "./$d/*" -not -path "*/$d/*")
		done
		( cd "$PROJECT_DIR" && "${args[@]}" -print | sed 's|^\./||' )
	fi
}

is_excluded() {
	[ "$INCLUDE_ALL" -eq 1 ] && return 1
	local path="$1" base d g
	base="$(basename "$path")"
	for d in "${EXCLUDE_DIRS[@]}"; do
		case "/$path/" in */"$d"/*) return 0 ;; esac
	done
	for g in "${EXCLUDE_GLOBS[@]}"; do
		# shellcheck disable=SC2254
		case "$base" in $g) return 0 ;; esac
	done
	return 1
}

file_size() { wc -c < "$1" | tr -d ' '; }

# Um ficheiro e "texto" se o grep nao o marcar como binario. Ficheiros vazios
# tambem passam (o grep devolve 1 nesse caso).
is_text() {
	[ -s "$1" ] || return 0
	LC_ALL=C grep -Iq . "$1" 2>/dev/null
}

lang_for() {
	case "${1##*.}" in
		c|h)                 echo c ;;
		cpp|cc|cxx|hpp|hh)   echo cpp ;;
		js|mjs|cjs)          echo javascript ;;
		ts)                  echo typescript ;;
		jsx)                 echo jsx ;;
		tsx)                 echo tsx ;;
		py)                  echo python ;;
		rb)                  echo ruby ;;
		php)                 echo php ;;
		go)                  echo go ;;
		rs)                  echo rust ;;
		java)                echo java ;;
		kt|kts)              echo kotlin ;;
		swift)               echo swift ;;
		sh|bash|zsh)         echo bash ;;
		sql)                 echo sql ;;
		html|htm)            echo html ;;
		css)                 echo css ;;
		scss|sass)           echo scss ;;
		json)                echo json ;;
		yml|yaml)            echo yaml ;;
		toml)                echo toml ;;
		xml)                 echo xml ;;
		md|markdown)         echo markdown ;;
		vue)                 echo vue ;;
		svelte)              echo svelte ;;
		env)                 echo dotenv ;;
		*)
			case "$(basename "$1")" in
				Makefile|makefile|GNUmakefile|*.mk) echo makefile ;;
				Dockerfile|Dockerfile.*)            echo dockerfile ;;
				*)                                  echo text ;;
			esac
			;;
	esac
}

# A cerca (fence) tem de ser maior do que qualquer sequencia de backticks
# dentro do ficheiro, senao o bloco de codigo parte-se a meio.
fence_for() {
	local longest
	longest="$(LC_ALL=C grep -oE '^`+' "$1" 2>/dev/null \
		| awk '{ if (length($0) > m) m = length($0) } END { print m + 0 }')"
	local n=3
	[ "${longest:-0}" -ge 3 ] && n=$(( longest + 1 ))
	printf '%*s' "$n" '' | tr ' ' '`'
}

echo "A analisar $PROJECT_DIR ..."

INCLUDED="$TMP_DIR/included"
SKIPPED="$TMP_DIR/skipped"
: > "$INCLUDED"
: > "$SKIPPED"

total_bytes=0
while IFS= read -r rel; do
	[ -n "$rel" ] || continue
	abs="$PROJECT_DIR/$rel"
	[ -f "$abs" ] || continue          # salta symlinks partidos e submodulos
	[ -r "$abs" ] || { printf '%s\tsem permissao de leitura\n' "$rel" >> "$SKIPPED"; continue; }
	is_excluded "$rel" && continue
	size="$(file_size "$abs")"
	if [ "$size" -gt "$MAX_FILE_BYTES" ]; then
		printf '%s\tdemasiado grande (%s KB)\n' "$rel" "$(( size / 1024 ))" >> "$SKIPPED"
		continue
	fi
	if ! is_text "$abs"; then
		printf '%s\tficheiro binario\n' "$rel" >> "$SKIPPED"
		continue
	fi
	printf '%s\t%s\n' "$rel" "$size" >> "$INCLUDED"
	total_bytes=$(( total_bytes + size ))
done < <(list_candidates | LC_ALL=C sort)

file_count="$(wc -l < "$INCLUDED" | tr -d ' ')"
skip_count="$(wc -l < "$SKIPPED" | tr -d ' ')"

if [ "$file_count" -eq 0 ]; then
	echo "erro: nao foi encontrado nenhum ficheiro de texto em '$PROJECT_DIR'" >&2
	exit 1
fi

# --------------------------------------------------------- divisao em partes ---
# Cada parte junta ficheiros inteiros ate ao limite; nenhum ficheiro e cortado.
assign_parts() {
	awk -F'\t' -v limit="$MAX_PART_BYTES" '
		BEGIN { part = 1; used = 0 }
		{
			cost = $2 + 200                       # margem para o cabecalho do ficheiro
			if (limit > 0 && used > 0 && used + cost > limit) { part++; used = 0 }
			used += cost
			print part "\t" $1 "\t" $2
		}
	' "$INCLUDED"
}
assign_parts > "$TMP_DIR/parts"
part_count="$(awk -F'\t' '{ if ($1 > m) m = $1 } END { print m + 0 }' "$TMP_DIR/parts")"

# arvore de directorios, construida a partir da lista (sem depender do `tree`)
build_tree() {
	cut -f1 "$INCLUDED" | awk -F'/' '
		{
			for (i = 1; i <= NF; i++) {
				path = ""
				for (j = 1; j <= i; j++) path = path $j (j < i ? "/" : "")
				if (!(path in seen)) {
					seen[path] = 1
					indent = ""
					for (k = 1; k < i; k++) indent = indent "    "
					printf "%s%s%s\n", indent, $i, (i < NF ? "/" : "")
				}
			}
		}
	'
}

human() { awk -v b="$1" 'BEGIN { if (b < 1024) printf "%d B", b; else if (b < 1048576) printf "%.1f KB", b/1024; else printf "%.1f MB", b/1048576 }'; }

# ------------------------------------------------------------- escrita ---
rm -f "$OUT_DIR/$SAFE_NAME"-parte-*.md "$OUT_DIR/$SAFE_NAME.md"
GENERATED=()

part=1
while [ "$part" -le "$part_count" ]; do
	if [ "$part_count" -eq 1 ]; then
		out="$OUT_DIR/$SAFE_NAME.md"
	else
		out="$(printf '%s/%s-parte-%02d.md' "$OUT_DIR" "$SAFE_NAME" "$part")"
	fi
	GENERATED+=("$out")

	{
		echo "# Projeto: $BUNDLE_NAME"
		echo
		if [ "$part_count" -gt 1 ]; then
			echo "**Parte $part de $part_count.**"
			echo
			if [ "$part" -lt "$part_count" ]; then
				echo "> Este e um dump do codigo-fonte dividido em $part_count partes."
				echo "> Le esta parte, confirma que recebeste, e espera pelas restantes"
				echo "> antes de analisares o projeto como um todo."
			else
				echo "> Ultima parte. Ja tens o projeto completo — podes analisar tudo em conjunto."
			fi
		else
			echo "> Dump completo do codigo-fonte deste projeto, gerado automaticamente."
		fi
		echo
		echo "- Gerado em: $(date '+%Y-%m-%d %H:%M')"
		echo "- Ficheiros no projeto: $file_count ($(human "$total_bytes"))"
		[ "$skip_count" -gt 0 ] && echo "- Ficheiros omitidos (binarios/grandes): $skip_count"
		echo

		if [ "$part" -eq 1 ]; then
			echo "## Estrutura do projeto"
			echo
			echo '```'
			echo "$BUNDLE_NAME/"
			build_tree | sed 's/^/    /'
			echo '```'
			echo
			if [ "$skip_count" -gt 0 ]; then
				echo "<details><summary>Ficheiros omitidos ($skip_count)</summary>"
				echo
				echo '```'
				awk -F'\t' '{ printf "%-50s %s\n", $1, $2 }' "$SKIPPED"
				echo '```'
				echo
				echo "</details>"
				echo
			fi
		fi

		echo "## Ficheiros"
		echo

		awk -F'\t' -v p="$part" '$1 == p { print $2 }' "$TMP_DIR/parts" | while IFS= read -r rel; do
			abs="$PROJECT_DIR/$rel"
			fence="$(fence_for "$abs")"
			echo "### \`$rel\`"
			echo
			printf '%s%s\n' "$fence" "$(lang_for "$rel")"
			cat "$abs"
			# garante que a cerca de fecho comeca numa linha nova
			[ -s "$abs" ] && [ -n "$(tail -c 1 "$abs")" ] && echo
			printf '%s\n' "$fence"
			echo
		done

		if [ "$part" -eq "$part_count" ]; then
			echo "---"
			echo
			echo "Fim do projeto \`$BUNDLE_NAME\`."
		fi
	} > "$out"

	part=$(( part + 1 ))
done

# ---------------------------------------------------------------- zip ---
if [ "$MAKE_ZIP" -eq 1 ]; then
	if command -v zip >/dev/null 2>&1; then
		zip_path="$OUT_DIR/$SAFE_NAME.zip"
		rm -f "$zip_path"
		( cd "$PROJECT_DIR" && cut -f1 "$INCLUDED" | zip -q -@ "$zip_path" )
		GENERATED+=("$zip_path")
	else
		echo "aviso: 'zip' nao esta instalado — a saltar o --zip" >&2
	fi
fi

# ------------------------------------------------------------- resumo ---
echo
echo "Pronto — $file_count ficheiros ($(human "$total_bytes")) em $part_count parte(s):"
for f in "${GENERATED[@]}"; do
	printf '  %s  (%s)\n' "$f" "$(human "$(file_size "$f")")"
done
if [ "$skip_count" -gt 0 ]; then
	echo
	echo "$skip_count ficheiro(s) omitidos (binarios ou > ${MAX_FILE_KB} KB) — listados no cabecalho da parte 1."
fi
echo
echo "Agora faz upload destes ficheiros no ChatGPT, por ordem."

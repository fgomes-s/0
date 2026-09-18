# Casa de pedra — plantas de arquitectura

Duas folhas A4 independentes, em desenho técnico a preto e branco, prontas a imprimir.
**Desenho esquemático: sem cotas e sem escala** — mostra a organização dos espaços, não medidas.

| Ficheiro | Conteúdo |
| --- | --- |
| `planta_piso0.pdf` | Folha 01/02 — Piso 0 (w.c., sala/cozinha, lavandaria, escritório, quintal) |
| `planta_piso1.pdf` | Folha 02/02 — Piso 1 (quarto, roupeiro, vão da escada) |
| `plantas.pdf` | As duas folhas no mesmo ficheiro (2 páginas) |
| `planta_piso0.svg`, `planta_piso1.svg` | Versões vetoriais editáveis |
| `gerar_plantas.py` | Gerador (sem dependências externas) |

## Características do desenho

- Formato A4 vertical (210 × 297 mm), margem de encadernação à esquerda, cartucho normalizado.
- Sem cadeias de cotas, sem áreas e sem escala declarada: as proporções entre divisões são
  coerentes, mas o desenho não se destina a ser medido (`NÃO ESCALAR O DESENHO`).
- Hierarquia de traço: corte de parede 0,5 mm · mobiliário 0,26 mm · tramas 0,10 mm.
- Alvenaria de pedra existente com trama de pedra irregular; paredes novas a cheio.
- Portas com sentido de abertura, vãos com aro e vidro, escada com linha de corte
  convencional e sentido de subida/descida, pavimento exterior em lajeta.
- Programa de compartimentos, legenda e notas técnicas em cada folha.

## Regenerar

```bash
python3 gerar_plantas.py     # escreve SVG + HTML + PDF na mesma pasta
```

O PDF é impresso com o Chromium em modo headless (procurado automaticamente nos
caminhos habituais). Sem Chromium, os SVG/HTML são criados na mesma.

A geometria está definida em metros no topo de `gerar_plantas.py` (constantes `T`, `MX0`,
`AX0`, etc.) e desenhada a 1:70, apenas para fixar proporções — esse valor não é impresso.
Para repor as cadeias de cotas, a escala gráfica e o quadro de áreas, ver o commit anterior
a este no histórico (`git show HEAD~1 -- plantas/gerar_plantas.py`).

> Desenho conceptual, a partir de uma planta de proposta e não de um levantamento. Antes de
> qualquer obra é necessário levantamento rigoroso e validação estrutural das paredes
> existentes.

# Casa de pedra — plantas de arquitectura

Duas folhas A4 independentes, em desenho técnico a preto e branco, prontas a imprimir.

| Ficheiro | Conteúdo |
| --- | --- |
| `planta_piso0.pdf` | Folha 01/02 — Piso 0 (w.c., sala/cozinha, lavandaria, escritório, quintal) |
| `planta_piso1.pdf` | Folha 02/02 — Piso 1 (quarto, roupeiro, vão da escada) |
| `plantas.pdf` | As duas folhas no mesmo ficheiro (2 páginas) |
| `planta_piso0.svg`, `planta_piso1.svg` | Versões vetoriais editáveis |
| `gerar_plantas.py` | Gerador (sem dependências externas) |

## Características do desenho

- Formato A4 vertical (210 × 297 mm), margem de encadernação à esquerda, cartucho normalizado.
- Escala **1:75**, com escala gráfica impressa em cada folha (o desenho mantém-se legível
  mesmo que a impressora ajuste a página).
- Cotas em metros, medidas em tosco: cadeias exteriores, vãos cotados e cotas parciais.
- Hierarquia de traço: corte de parede 0,5 mm · mobiliário 0,26 mm · tramas 0,10 mm.
- Alvenaria de pedra existente com trama de pedra irregular; paredes novas a cheio.
- Portas com sentido de abertura, vãos com aro e vidro, escada com linha de corte
  convencional e sentido de subida/descida.
- Quadro de áreas, legenda e notas técnicas em cada folha.

## Medidas adoptadas

Volume principal 5,80 × 8,20 m exteriores, paredes de pedra de 0,55 m; anexo/quintal
4,90 × 6,80 m com muros de 0,30 m; divisórias novas de 0,12 m. Escada de 15 espelhos
(0,187 m) e 14 cobertores (0,27 m), para um pé-direito de 2,60 m no piso 0.

Área útil: 43,22 m² (piso 0) + 29,16 m² (piso 1) = **72,38 m²**; quintal 17,27 m².

## Regenerar

```bash
python3 gerar_plantas.py     # escreve SVG + HTML + PDF na mesma pasta
```

O PDF é impresso com o Chromium em modo headless (procurado automaticamente nos
caminhos habituais). Sem Chromium, os SVG/HTML são criados na mesma.

> Desenho conceptual: as medidas são coerentes entre si mas foram arbitradas a partir de
> uma planta de proposta, não de um levantamento. Antes de qualquer obra é necessário
> levantamento rigoroso e validação estrutural das paredes existentes.

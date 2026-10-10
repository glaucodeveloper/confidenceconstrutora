# Confidence CMS: vídeos por registro e CRUD ao lado da ordenação

Atualização integrada à versão atual do `index.html` (blob Git `575aea1e1747bc987f539600789dc8fe7456f945`). Preserva o cache local completo, Markdown, reordenação, carrossel mobile, desfazer e salvamento manual.

## Verificação de mesclagem dos registros publicados

Na leitura de `data/site-data.json`, foram encontrados seis registros de obra. Não há IDs de atividades ou imagens repetidos entre as obras de Ubaitaba. Porém, o registro `centro-canoagem-ubaitaba-7e5b674b-766e-43b0-8d8b-166266eac3c5`, dentro de “Reforma do Centro de Canoagem”, tem descrição sobre uma fábrica da Coca-Cola. Essa descrição não corresponde ao nome da obra e pode indicar conteúdo mesclado ou atribuído à obra errada. Também existe a obra `obra-mv1rfng8` com nome, cidade, tipo e resumo iguais a `.` e sem atividades.

O instalador deste pacote altera somente `index.html` e este README. Ele não altera `data/site-data.json` nem exclui mídia; os dois registros suspeitos precisam de conferência editorial antes de qualquer correção de conteúdo.

## Vídeos no registro

Os vídeos passaram a pertencer a `works[].activities[].videos[]`, no **mesmo registro de execução** que contém as fotos. A faixa fina de miniaturas ocupa a lateral direita do carrossel da atividade em desktop e torna-se horizontal dentro do registro em mobile. Clicar numa miniatura abre um player ampliado no backdrop. Cada vídeo possui seu título e `muted` (som inicial ligado ou mutado).

A Home e o nível geral da obra deixam de exibir os vídeos dessas áreas. Entradas legadas em `SITE_DATA.videos` ou `work.videos` **não são apagadas nem migradas automaticamente**, para não associar indevidamente um arquivo à atividade errada.

## Ações CRUD na alça de ordem

No CMS, tanto os cards de obras como os registros têm ícones posicionados lado a lado: **Ordenar**, **Adicionar**, **Editar** e **Remover**.

- **Obra**: Adicionar abre a criação guiada de obra; Editar abre formulário integrado com nome, município, estado, tipo, resumo e troca opcional de capa; Remover oculta a obra e seus registros na visualização do editor.
- **Registro**: Adicionar abre a seção guiada para criar um registro depois do card selecionado; Editar abre formulário inline de título/descrição, mantendo fotos e vídeos; Remover exclui o registro da obra no rascunho.

Alterações e remoções têm **Desfazer** na seção de pendências, enquanto os arquivos existentes continuam no repositório. Nenhuma das ações faz upload ou grava JSON automaticamente. O editor local segue priorizando a versão local salva em `localStorage`, com mídias pendentes em IndexedDB, quando o navegador está autenticado no modo de edição.

## Publicar no Linux Manjaro

```bash
sudo pacman -S --needed git unzip
cd ~/Downloads
unzip -o confidence-cms-video-registro-crud.zip -d confidence-cms-video-registro-crud
bash confidence-cms-video-registro-crud/apply-video-registro-crud-manjaro.sh
```

O script lê o último `index.html` no `main`, confere o blob SHA esperado e interrompe caso o arquivo tenha sido atualizado por outra fonte. Em caso de divergência, **não force**: solicite uma build mesclada à versão remota atual. Não sobrescreve `data/site-data.json` nem assets.

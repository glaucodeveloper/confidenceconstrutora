# Confidence CMS

CMS visual próprio aplicado ao site institucional da Confidence Construtora, servido como SPA no GitHub Pages e persistido via GitHub Contents API com autenticação por PAT.

## Escopo

- **Público:** leitura de `data/site-data.json`, navegação do portfólio de obras, mapa de atuação, cards, páginas de detalhe, galerias, certificações, clientes e contatos, sem autenticação.
- **Administração:** `#/login` com PAT em `sessionStorage`; edição de textos e imagens por hover/clique, criação de obras e registros, galeria complementar, edição do painel de contato.
- **Persistência:** alterações mantidas como rascunho, com backup local de versões e **Desfazer** por item. O botão **Salvar alterações** no rodapé consolida o JSON e envia os arquivos pendentes para `assets/uploads/`.
- **Logout:** remove PAT do `sessionStorage` e `localStorage`, desmonta controles e recarrega a página; solicita confirmação quando há rascunho não salvo.

## Edição diretamente nos elementos

O botão de editar texto ativa `contenteditable` no próprio elemento destacado. Um pequeno menu flutuante permite negrito, itálico, sublinhado, **Aplicar** ou **Cancelar**. `Ctrl+Enter` confirma; `Esc` cancela. Os campos de criação de obra e registro usam `input` e `textarea` reais, destacados no hover/foco, sem diálogos de prompt. A inclusão de nova informação de contato utiliza um formulário inline.

## Certificação ISO 9001

O layout textual anteriormente representado por `div.iso-reference-logo` foi substituído por uma **imagem SVG local** (`assets/iso-9001-reference.svg`). A imagem é marcada com `data-cms-key="iso-9001-logo"` e pode ser substituída pelo CMS como as outras imagens do site. É apenas uma **referência gráfica à norma**, não um selo de certificação emitido pela ISO.

## Obras, registros e imagens

`works[]` no arquivo `data/site-data.json` contém informações de cada obra (`slug`, `name`, `city`, `state`, `type`, `summary`, `cover`, `photos`, `activities`).

Cada registro de `activities[]` permite uma ou várias fotos:

```json
{
  "id": "registro-001",
  "title": "Preparação do terreno",
  "description": "Movimentação e regularização de solo na frente de serviço.",
  "image": "assets/obras/foto-01.jpg",
  "images": ["assets/obras/foto-01.jpg", "assets/obras/foto-02.jpg"],
  "imagePositions": [{"x": 50, "y": 50}, {"x": 70, "y": 35}]
}
```

- `image` continua sendo a primeira foto (compatibilidade com registros antigos).
- `images[]` guarda todas as fotos da sessão; registros antigos com apenas `image` continuam funcionando.
- **Adicionar registro** abre um bloco inline com título, descrição e seleção/arraste de múltiplas imagens.
- Registros já criados ganham **+ Foto**, com possibilidade de retirar imagens individualmente.
- As fotos de cada registro são exibidas em um **carrossel**, com uma imagem principal, miniaturas clicáveis, setas de navegação, indicação de posição e swipe horizontal no celular. O layout mantém a descrição do registro e não desloca horizontalmente a página, inclusive em telas estreitas de 320 px.

No modo de edição, **Ajustar posição** permite arrastar a imagem ou alterar o enquadramento por controles horizontal e vertical. Os ajustes são registrados por imagem em `imagePositions[]` no próprio registro, sem alterar o arquivo, e permanecem no rascunho com **Desfazer** antes de Salvar alterações. O array utiliza posições em porcentagem (0 a 100), alinhadas à ordem de `images[]`.

Cada obra também admite `gallery[]`, um array independente de imagens complementares. A seção **Galeria da obra** possui um slot **+ Adicionar fotos** para selecionar ou arrastar vários arquivos e retirar imagens existentes no modo edição. Os arquivos só são enviados ao GitHub no salvamento consolidado. A galeria existente, a capa e os registros originais são preservados.

## Salvamento e conflitos

Toda modificação cria entrada de rascunho com botão **Desfazer** no rodapé. O `data/site-data.json` somente é publicado após **Salvar alterações**. Na persistência, o CMS consulta o SHA atual do arquivo remoto usando nonce na URL (sem cabeçalhos extras incompatíveis com CORS). Se houver HTTP 409, busca o SHA novamente e tenta uma vez mais, sem descartar o rascunho.

Uploads usam nomes normalizados com timestamp e sufixo aleatório em `assets/uploads/<ano>/`.

## Estrutura

```text
index.html
README.md
data/site-data.json
assets/
  iso-9001-reference.svg
  uploads/
```

## Publicação desta atualização

`apply-cms-multifoto.ps1` publica em um único commit apenas `index.html`, `README.md` e `assets/iso-9001-reference.svg`. **Não modifica** o JSON remoto, nem apaga imagens existentes. As alterações de conteúdo feitas pelo CMS são salvas depois, a partir da interface autenticada.

## Imagens com recuperação automática

Imagens comuns e de fundo (hero, institucional e painéis CMS) são acompanhadas de um mecanismo de recuperação que não modifica as URLs armazenadas no JSON.

- Após falha de rede ou timeout, o navegador repete o carregamento com intervalos crescentes, com limite de tentativas.
- O retry altera somente a URL efetivamente usada na visualização, adicionando um identificador de tentativa quando apropriado; o dado salvo permanece como estava.
- Ao atingir o limite sem sucesso, aparece **Tentar novamente**, permitindo outra rodada manual sem quebrar a página.
- Os retries não exigem autenticação, não fazem commits e não enviam cabeçalhos de requisição incompatíveis com CORS.

## Responsividade e acessibilidade do carrossel

- Layout fluido para desktop e mobile, sem overflow horizontal da página, testado em 320, 375, 390 e 1440 px.
- Miniaturas em faixa com rolagem horizontal independente; imagem principal com proporção fluida no mobile.
- Botões de navegação e edição com alvo de toque de pelo menos 44 px; swipe lateral na imagem e rolagem vertical normal da página.
- Navegação por setas de teclado, rótulos acessíveis, contagem da imagem ativa e preferência de movimento reduzido respeitada.
- Foto e posição selecionadas são preservadas quando o registro é atualizado em rascunho; remover foto também remove seu enquadramento correspondente.

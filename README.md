# Confidence CMS

Sistema de gerenciamento de conteúdo próprio desenvolvido para o site institucional da Confidence Construtora, integrado diretamente ao repositório publicado via GitHub Pages.

O projeto transforma uma SPA estática em uma aplicação institucional editável, mantendo leitura pública dos conteúdos e restringindo operações de escrita ao modo administrativo autenticado por GitHub Personal Access Token (PAT).

## Escopo

O CMS opera sem backend dedicado. O próprio repositório GitHub funciona como camada de persistência, armazenamento de assets, histórico e publicação.

A aplicação pública utiliza:

- `index.html` como SPA e interface de edição;
- `data/site-data.json` como fonte estruturada de conteúdo;
- `assets/` como armazenamento das imagens e arquivos;
- GitHub Pages como publicação;
- GitHub API como mecanismo autenticado de escrita.

A leitura do site não exige autenticação. O PAT é usado somente quando o modo administrativo precisa gravar alterações no repositório.

## Conteúdo administrável

O CMS permite editar diretamente sobre a interface publicada:

- textos institucionais;
- títulos e descrições;
- imagens e backgrounds;
- informações de contato;
- portfólio de obras;
- dados de cada obra;
- registros fotográficos de execução;
- títulos e descrições técnicas de registros.

Elementos editáveis são identificados visualmente durante o modo administrativo e podem ser alterados por interação direta.

## Obras

Cada obra é representada em `data/site-data.json` com estrutura própria:

- `slug`;
- nome;
- cidade;
- estado;
- tipo;
- resumo;
- imagem de capa;
- galeria;
- registros de execução.

Os mesmos dados alimentam automaticamente:

- cards de **Obras e atuação**;
- mapa de municípios;
- slideshow;
- páginas `#/obra/<slug>`;
- galeria;
- sequência de registros da execução.

## Criação de obras

No modo administrativo, a seção de obras exibe um card **Adicionar obra**.

Esse fluxo abre `#/nova-obra`, uma página guiada onde os campos respondem a hover e clique.

Campos disponíveis:

- nome da obra;
- cidade;
- estado;
- tipo;
- resumo;
- capa.

A obra é adicionada primeiro ao rascunho do CMS. Depois do salvamento consolidado, passa a integrar `works[]` em `data/site-data.json`.

## Registros de execução

Cada obra pode possuir registros independentes contendo:

- identificador;
- título;
- descrição técnica;
- imagem.

No modo de edição é possível:

- adicionar registro;
- remover registro;
- editar textos;
- alterar imagens.

As novas imagens são preparadas em rascunho e enviadas para `assets/uploads/` somente durante o salvamento consolidado.

### Isolamento dos conteúdos por obra

Os textos editáveis dentro de uma página de obra são identificados também pelo `slug` da obra. Assim, seções com o mesmo `id` HTML — por exemplo, `#execucao` — não compartilham o mesmo override do CMS: editar um título ou uma descrição em uma obra não altera os slots das demais.

Na inicialização, o CMS migra overrides antigos `text:execucao:*` para o escopo da obra `areninha-barra-do-choca`, preservando os valores legados dessa página e removendo as chaves globais ambíguas do estado carregado. A migração passa a ser persistida em `data/site-data.json` no próximo salvamento administrativo.

### Verificações do fluxo de obras

Foram verificados visualmente os casos abaixo na publicação e em uma execução local:

- abrir Areninha Barra do Choça, Seabra e Canoagem Ubaitaba e confirmar que cada página mostra títulos, descrições, imagens e quantidade de registros próprios;
- percorrer registros do início ao fim, incluindo os últimos IDs de cada obra;
- carregar a migração dos overrides legados e confirmar que os valores são preservados sob a chave da Areninha, sem chaves globais `text:execucao:*` restantes;
- conferir larguras desktop e móveis (1280, 768, 390 e 320 px), sem rolagem horizontal;
- conferir as URLs das 50 imagens referenciadas, sem imagens inexistentes.

O teste visual não executa um salvamento autenticado na publicação nem envia dados de teste ao repositório. A gravação final deve ser validada em ambiente administrativo com PAT autorizado, verificando que somente o arquivo JSON e os assets esperados sejam alterados.

## Rascunho, backups e desfazer

As alterações do CMS não são persistidas imediatamente.

Cada nova modificação:

1. cria uma versão de backup do conteúdo anterior;
2. entra no estado de rascunho;
3. aparece na lista de alterações pendentes;
4. recebe seu próprio botão **Desfazer**.

Os backups da sessão são mantidos localmente durante a edição e limitados às versões recentes.

Tipos de alteração cobertos:

- texto;
- imagem;
- informação de contato;
- nova informação;
- remoção de informação;
- nova obra;
- novo registro;
- remoção de registro.

Alterações repetidas no mesmo conteúdo são agrupadas para que o botão **Desfazer** volte ao estado anterior ao início daquela edição.

## Salvamento consolidado

Quando existe qualquer modificação pendente, o CMS mostra uma seção **Rascunho do CMS** no final da página.

Essa seção apresenta:

- quantidade de alterações pendentes;
- lista das mudanças;
- botão **Desfazer** individual;
- botão **Salvar alterações**.

Ao salvar:

1. assets pendentes são enviados para `assets/uploads/`;
2. URLs temporárias são substituídas pelas URLs persistidas;
3. o estado atualizado é consolidado em `data/site-data.json`;
4. o CMS cria o commit de conteúdo;
5. a lista de alterações pendentes é limpa.

Se houver alterações não salvas e o usuário tentar recarregar ou sair, a aplicação solicita confirmação.

## Contato

O painel de contato também é administrável.

É possível:

- editar título;
- editar descrição;
- trocar background;
- alterar valores existentes;
- adicionar informações;
- remover informações.

Os itens ficam em `contactPanel.items`.

## Autenticação

A rota administrativa é:

```text
#/login
```

Após validação do PAT, o modo de edição é ativado.

Sem PAT:

- a toolbar administrativa não permanece montada;
- não são exibidos controles de escrita;
- o site funciona somente para leitura.

Ao usar **Sair**:

- o PAT é removido de `sessionStorage`;
- o PAT é removido de `localStorage`;
- o modo de edição é desativado;
- os controles administrativos são removidos;
- a rota volta para `#/`;
- a página é recarregada.

Se houver um rascunho não salvo, o CMS pede confirmação antes de descartá-lo.

## Estrutura

```text
/
├── index.html
├── README.md
├── data/
│   └── site-data.json
└── assets/
    ├── ...
    └── uploads/
```

## Estrutura principal do conteúdo

`data/site-data.json` centraliza:

```text
brand
works
contactPanel
text
images
updatedAt
```

## Objetivo

O objetivo é fornecer à Confidence Construtora autonomia para administrar o site institucional e o portfólio de obras sem banco de dados dedicado, painel externo ou CMS tradicional.

A arquitetura mantém a simplicidade de um site estático em GitHub Pages, mas adiciona edição visual, upload de assets, versionamento, rascunho, desfazer e persistência diretamente pelo GitHub.

## Salvamento na página inicial

O estado de rascunho também é exibido explicitamente na página inicial.

Sempre que uma modificação é realizada na Home — incluindo textos institucionais, imagens, backgrounds ou informações de contato — o CMS monta uma área **Rascunho do CMS** imediatamente antes do footer.

Essa área contém:

- quantidade de alterações pendentes;
- lista das modificações;
- botão **Desfazer** para cada conteúdo alterado;
- botão **Salvar alterações** para consolidar o rascunho no repositório.

O painel é remontado automaticamente caso a Home seja renderizada novamente durante a edição, evitando que a interface de salvamento desapareça após alterações estruturais.

## Tratamento de conflito de versão

O CMS utiliza o SHA atual de `data/site-data.json` exigido pela GitHub Contents API.

Antes de cada salvamento consolidado, o site busca novamente o arquivo remoto usando um parâmetro anti-cache único na URL. A chamada mantém somente os headers aceitos pelo CORS da API do GitHub.

Se o GitHub responder `409 Conflict` indicando que o SHA mudou entre a leitura e a escrita:

1. o rascunho permanece intacto;
2. o CMS não limpa a lista de alterações;
3. o SHA remoto é consultado novamente;
4. o PUT é repetido automaticamente uma vez com a versão atual;
5. o rascunho só é marcado como salvo depois de uma resposta de sucesso do GitHub.

Isso evita que um SHA armazenado em cache impeça o salvamento e mantém o conteúdo pendente disponível caso a segunda tentativa também falhe.

### Compatibilidade CORS da API do GitHub

As chamadas executadas diretamente pelo navegador não enviam `Cache-Control` nem `Pragma`, pois esses headers não fazem parte da lista aceita pelo preflight CORS da API do GitHub.

A atualização do SHA usa um parâmetro único na query string para impedir reutilização da URL anterior, preservando o retry automático de conflitos `409`.

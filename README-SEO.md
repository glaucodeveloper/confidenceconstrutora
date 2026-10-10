# Confidence Construtora — SEO e identidade visual

Esta atualização foi projetada para ser executada **sobre o `main` atual** do repositório `glaucodeveloper/confidenceconstrutora`. Ela não substitui o CMS por uma cópia antiga e não altera `data/site-data.json`, as imagens existentes, o `CNAME` ou o histórico de edições.

## Escopo

- Domínio canônico `https://construtoraconfidence.com/`, conforme o `CNAME` do próprio repositório.
- `title`, `description`, `canonical`, `robots`, Open Graph e Twitter Cards para a Home.
- JSON-LD `GeneralContractor` + `WebSite` com os dados de contato já existentes no CMS.
- Índice público e indexável das obras em `/obras/`.
- Uma página HTML estática indexável por obra em `/obras/<slug>/`, gerada a partir de `data/site-data.json`.
- Fotos, títulos, resumo, município e descrições de atividades reais das obras, sem inventar serviços ou status.
- JSON-LD de `WebPage` e `BreadcrumbList` para cada obra.
- `sitemap.xml` com Home, índice e todas as obras atuais.
- `robots.txt` que aponta para o sitemap.
- Logos oficiais azul/clara armazenadas localmente em `assets/branding/`; as URLs desses dois arquivos já eram usadas pelo CMS no projeto original. Qualquer logo personalizada pela edição permanece preservada.
- Favicon PNG quadrado para ícone do site (símbolo "C"; não é o logotipo completo).
- Título da aba coerente com a obra atualmente aberta na SPA.
- Links nas páginas estáticas para abrir a galeria interativa e registros no CMS já existente.

## Logo

A implementação usa as **duas versões oficiais já referenciadas pelo repositório**:

- `https://github.com/glaucodeveloper/proposta-confidence/blob/main/imagens/logo_oficial_aplicacao_azul.png`
- `https://github.com/glaucodeveloper/proposta-confidence/blob/main/imagens/logo_oficial_aplicacao_clara.png`

O instalador baixa os arquivos de um commit fixo e **verifica os SHA dos dois blobs** antes de fazer commit; caso os bytes sejam diferentes, ele interrompe a publicação. A captura do HTML do domínio antigo não disponibilizou o caminho exato da logo original; não se afirma que o logo foi extraído do servidor antigo. São os logotipos oficiais que a aplicação já utiliza.

## Instalação no Manjaro

```bash
sudo pacman -S --needed git curl python unzip nodejs
cd ~/Downloads
unzip -o confidence-seo-logo-manjaro.zip -d confidence-seo-logo-manjaro
bash confidence-seo-logo-manjaro/apply-seo-manjaro.sh --dry-run
bash confidence-seo-logo-manjaro/apply-seo-manjaro.sh
```

O script clona `main` imediatamente antes de modificar, verifica `CNAME`, baixa e verifica logos, modifica o HTML **pontualmente**, gera as páginas e sitemap e cria um único commit. Ele verifica novamente o HEAD antes de publicar: se alguém tiver alterado o repositório enquanto ele trabalha, cancela o push.

## Publicação automática após edição de obras no CMS

O workflow `.github/workflows/seo-publish.yml` foi incluído para regenerar páginas indexáveis sempre que houver um push em `main`, inclusive após `Salvar alterações` no CMS.

Para habilitar esta publicação contínua, configure **GitHub > Settings > Pages > Build and deployment > Source: GitHub Actions**. Assim o workflow publica o site com as páginas regeneradas. Se a publicação ainda estiver no modo "Deploy from a branch", as páginas geradas no commit inicial são publicadas normalmente, mas as páginas de novas obras não serão automaticamente atualizadas até que você execute novamente o gerador ou migre para GitHub Actions.

O CNAME existente não é modificado.

## Operação local do gerador

No checkout do repositório:

```bash
python3 scripts/seo/generate.py .
```

Isso atualiza `sitemap.xml`, `robots.txt` e `obras/*/index.html` a partir do JSON mais recente. Nunca grava o JSON nem publica alterações automaticamente.

## Registro e indexação

Depois da publicação, cadastre `https://construtoraconfidence.com/` no Google Search Console e envie:

`https://construtoraconfidence.com/sitemap.xml`

A indexação efetiva depende dos buscadores e da configuração correta do DNS/HTTPS; metadados e sitemap não garantem ranking ou indexação imediata.


## Limitação de permissões e regeneração

O instalador PowerShell **não instala workflows por padrão**, porque o Git Credential Manager pode usar uma credencial OAuth sem permissão `workflow`. Nesse modo, publique Pages a partir de `main/(root)` e reexecute o script após alterações no JSON para regenerar o sitemap e as páginas estáticas. Use `-InstallWorkflow` somente com credencial que permita gerenciar Workflows; nesse modo escolha GitHub Actions como fonte do Pages.

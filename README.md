# TikTok Video Uploader (S3 to TikTok)

Este projeto automatiza o upload de vídeos da Bíblia de um bucket AWS S3 para o TikTok, utilizando a biblioteca `tiktok-uploader` com Playwright.

## Funcionalidades

1.  Busca o vídeo mais antigo na pasta `biblia/videos/prontos/` no S3.
2.  Extrai o número do capítulo do nome do arquivo (ex: `Gênesis_1_...mp4` -> Capítulo 1).
3.  Faz o upload para o TikTok com a descrição: `"Hoje vamos ler Genesis X..."`.
4.  Move o vídeo para `biblia/videos/postados/` após o sucesso.

## Pré-requisitos

*   [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados.
*   Um arquivo `cookies.txt` com seus cookies do TikTok (formato Netscape).
*   Credenciais da AWS (Access Key e Secret Key) com permissão de leitura/escrita no bucket S3.

## Configuração

1.  Coloque seu arquivo `cookies.txt` na raiz deste projeto.
2.  Crie um arquivo `.env` na raiz do projeto com as configurações do seu bucket:

```env
S3_BUCKET_NAME=seu-nome-de-bucket
AWS_REGION=us-east-1
```

*Nota: Como o projeto rodará em uma EC2 com permissões (IAM Role), não é necessário passar `AWS_ACCESS_KEY_ID` ou `AWS_SECRET_ACCESS_KEY` no arquivo `.env`. O script detectará as permissões automaticamente.*

## Como Rodar

Para buildar a imagem e iniciar o processo de upload:

```bash
docker-compose up --build
```

O container irá:
1. Instalar todas as dependências do sistema e navegadores necessários.
2. Baixar o vídeo mais antigo.
3. Realizar o upload em modo headless (sem interface gráfica).
4. Mover o vídeo no S3.
5. Encerrar a execução ao terminar.

## Estrutura do S3 Esperada

*   `biblia/videos/prontos/`: Local onde você deve colocar os vídeos para serem postados.
*   `biblia/videos/postados/`: Local para onde o script moverá os vídeos após o upload.

## Observações

*   O script extrai o capítulo baseado no padrão `Nome_Capitulo_ID.mp4`.
*   Certifique-se de que o `cookies.txt` é válido, caso contrário o upload falhará.

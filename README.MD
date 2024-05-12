# Model Manager

## Descrição

Model Manager é uma aplicação construída em Flask, projetada para gerenciar e analisar modelos de machine learning de forma eficiente e eficaz. A aplicação é empacotada em um contêiner Docker para facilitar a distribuição e a implantação em qualquer ambiente, mantendo a consistência entre os desenvolvimentos e os ambientes de produção.

## Pré-requisitos

Antes de iniciar, certifique-se de que o Docker está instalado em sua máquina. Caso não tenha o Docker instalado, você pode baixá-lo e instalá-lo seguindo as instruções no [site oficial do Docker](https://docs.docker.com/get-docker/).

## Como Usar

Siga as instruções abaixo para colocar a aplicação Model Manager em funcionamento usando Docker.

### Construção da Imagem Docker

Abra o terminal e navegue até o diretório onde está o Dockerfile. Execute o comando abaixo para construir a imagem Docker do projeto:

Crie a rede
```bash
docker network create minha-rede
```

Construa a imagem
```bash
docker build -t model-manager .
```

Depois execute

```bash
docker run -d -p 5000:5000 --network bridge model-manager
```
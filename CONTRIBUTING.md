flask# Como Contribuir - Seu Passaporte de Entrada

Estamos felizes em receber você aqui e saber que está interessado em contribuir para o nosso projeto. Como um projeto de código aberto, cada contribuição é valorizada e ajuda a impulsionar o crescimento e a qualidade do nosso trabalho. Este guia foi criado para orientá-lo sobre como você pode participar e fazer parte da nossa comunidade de desenvolvimento. Estamos ansiosos para ver suas contribuições e trabalhar juntos para tornar nosso projeto ainda melhor!

## Código de Conduta

Para garantir um ambiente respeitável e inclusivo, leia e siga nosso [Código de Conduta](./CODE_OF_CONDUCT.md).

## Começando a Contribuir

Contribuir para o nosso projeto é fácil e estamos ansiosos para receber suas contribuições! Antes de entrarmos nos passos para instalação da aplicação, você precisará configurar algumas ferramentas e preparar seu ambiente de desenvolvimento.

Aqui está o que você precisa:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started/), para utilização de contâineres. É opcional, mas recomendamos o seu uso.
- Caso opte por não utilizar Docker:
  - [Python v3.12](https://www.python.org/downloads/release/python-3120/)
  - [MySQL](https://dev.mysql.com/downloads/mysql/)

## Instalação

Vamos indicar aqui duas maneiras de instalar:

1. utilizando o Docker
2. utilizando um ambiente virtual `venv`.

Mas, primeiro, vamos realizar algumas configurações comuns à essas maneiras de instalação.

1. clone o repositório e o acesse.

   ```bash
   git clone https://github.com/Bug-Busters-F/alfalog-backend

   cd alfalog-backend
   ```

2. Configure as variáveis de ambiente

    ```sh
    cp .env.template .env
    ```

3. Abra o arquivo `.env` e edite as credenciais de conexão com o banco de dados.

    ```sh
    # ...
    APP_DB_HOST=   # database host
    APP_DB_USER=   # database user
    APP_DB_PASS=   # database password
    APP_DB_NAME=   # database name
    APP_DB_PORT=   # database port
    ```

### Instalação utilizando Docker

```sh
docker compose up --build -d
```

Esse comando irá

- criar a imagem Docker deste projeto
- buscar a imagem do banco de dados no repositório Docker
- Iniciar um container do banco de dados
- Iniciar um container deste projeto e criar as entidades no banco de dados.

O Flask está disponível em: [http://localhost:5000](http://localhost:5000)

### Instalação utilizando um ambiente virtual `venv`

1. Crie o ambiente virtual

   ```sh
   python -m venv venv

   # Windows - ative o ambiente
   source venv/Scripts/activate

   # Linux - ative o ambiente
   . venv/bin/activate

   # Mac - ative o ambiente
   source venv/bin/activate
   ```

2. Instale as dependências

   ```sh
   pip install -r requirements.txt
   ```

3. Configuração do banco de dados. Nessa etapa, você precisará criar ou já ter um banco de dados e usuário configurado. Se ainda não tiver um banco de dados, crie na sua instância do MySQL:

   ```sql
   CREATE DATABASE alfalog;

   CREATE USER 'alfalog'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON alfalog.* TO 'alfalog'@'localhost';
   FLUSH PRIVILEGES;
    ```

4. Crie o banco de dados e as tabelas automaticamente

   ```sh
   python -m database.create # executa database/create como um módulo Python.
   ```

5. Execute a aplicação

   ```sh
   flask run
   ```

O Flask está disponível em: [http://localhost:5000](http://localhost:5000)

## Importação de Dados do COMEX

Para importar os dados de exportações e importações, além de dados secundários como UFs (Unidades Federativas), da base do COMEX, siga os seguintes passos.

1. Abra o [Google Colab](https://colab.research.google.com/drive/1WRSAEERIYsReXWyuLLLTs28WkV41tFyW?usp=sharing) e execute a limpeza dos dados.

2. Em seguida, encontre dois arquivos .csv no seu Google Drive no diretório `/comex_data`

3. Faça o download dos dois arquivos e copie-os para uma pasta na raiz do projeto chamada `/data` com os seguintes nomes:

    ```sh
    # arquivo limpo de exportações
    dados_comex_EXP_2014_2024.csv
    # arquivo limpo de importações
    dados_comex_IMP_2014_2024.csv
    ```

4. Agora você pode importar os dados do COMEX executando o seguinte comando:

    ```sh
    flask comex update

    # execute este comando para conhecer as opções
    flask comex update --help
    ```

5. Caso queira importar os dados de uma única entidade, execute:

    ```sh
    flask comex update <nome-entidade>

    # execute para saber as entidades existentes
    flask comex update --help

    # Por exemplo:
    flask comex update importacoes # para dados da importação
    ```

## Testes

A cada atualização é recomendado rodar todos os testes a fim de garantir o funcionamento do programa.

```sh
pytest
```

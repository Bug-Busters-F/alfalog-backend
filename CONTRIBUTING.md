flask# Como Contribuir - Seu Passaporte de Entrada

Estamos felizes em receber você aqui e saber que está interessado em contribuir para o nosso projeto. Como um projeto de código aberto, cada contribuição é valorizada e ajuda a impulsionar o crescimento e a qualidade do nosso trabalho. Este guia foi criado para orientá-lo sobre como você pode participar e fazer parte da nossa comunidade de desenvolvimento. Estamos ansiosos para ver suas contribuições e trabalhar juntos para tornar nosso projeto ainda melhor!

## Código de Conduta

Para garantir um ambiente respeitável e inclusivo, leia e siga nosso [Código de Conduta](./CODE_OF_CONDUCT.md).

## Começando a Contribuir

Contribuir para o nosso projeto é fácil e estamos ansiosos para receber suas contribuições! Antes de entrarmos nos passos para instalação da aplicação, você precisará configurar algumas ferramentas e preparar seu ambiente de desenvolvimento.

Aqui está o que você precisa:

- Uma conta no [GitHub](https://github.com/)
- O *version control system* [Git](https://git-scm.com/) instalado.
- Um IDE para o desenvolvimento. Recomendamos o [IntelliJ IDEA](https://www.jetbrains.com/idea/).
- ..................
- O banco de dados [MySQL](https://dev.mysql.com/downloads/mysql/) configurado, pois o projeto utiliza o MySQL para armazenamento de dados.

### Instalação

O primeiro passo é clonar o repositório do projeto para o seu ambiente local.

1. Abra um terminal.
2. Execute o seguinte comando para clonar o repositório:

   ```bash
   git clone https://github.com/Bug-Busters-F/alfalog-backend
   ```

3. Navegue até o diretório do projeto:

   ```bash
   cd alfalog-backend
   ```


3. Indicamos o uso de um ambiente virtual, como o [venv](https://docs.python.org/3/library/venv.html)

    ```sh
    python -m venv venv

    # Windows - ative o ambiente
    source venv/Scripts/activate

    # Linux - ative o ambiente
    . venv/bin/activate

    # Mac - ative o ambiente
    source venv/bin/activate
    ```

4. Instale as dependências

    ```sh
    pip install -r requirements.txt
    ```

5. Configuração do banco
  1. Docker
        Esta é a maneira mais rápida e fácil, pois o Docker gerencia a criação e execução do container do banco de dados MySQL

        ```
            docker compose up --build -d mysql_alfalog_data
        ```

        Observação: Este comando Docker apenas inicia o serviço do banco de dados. O aplicativo Flask ainda será executado localmente (Passo 7). A configuração de conexão no arquivo .env pode não ser necessária ou será preenchida com valores padrão adequados para o ambiente Docker.


    2. Configure as variáveis de ambiente

        ```sh
        cp .env.template .env
        ```

        1. Nessa etapa, você precisará criar ou já ter um banco de dados e usuário configurado. Se ainda não tiver um banco de dados, crie na sua instância do MySQL:

            ```sql
            CREATE DATABASE alfalog;
            ```

        2. Caso criar um usuário específico para acesso ao banco de dados, execute o seguinte:

            ```sql
            CREATE USER 'alfalog'@'localhost' IDENTIFIED BY 'password';

            GRANT ALL PRIVILEGES ON alfalog.* TO 'alfalog'@'localhost';
            FLUSH PRIVILEGES;
            ```

        3. Abra o arquivo `.env` e edite as credenciais de conexão com o banco de dados.

            ```sh
            # ...
            DB_HOST=   # database host
            DB_USER=   # database user
            DB_PASS=   # database password
            DB_NAME=   # database name
            ```

6. Crie o banco de dados e as tabelas automaticamente

    ```sh
    python -m database.create # executa database/create como um módulo Python.
    ```

   1. Opcionalmente, você pode executar os comandos SQL em `database/seed.sql` diretamente no Banco de Dados para testes

7. Va até o [Google Colab](https://colab.research.google.com/drive/1WRSAEERIYsReXWyuLLLTs28WkV41tFyW?usp=sharing) da limpeza e execute a limpeza dos dados, após executado, será salvo dois arquivos .csv no seu Google Drive no diretório /comex_data
    

8. Após baixar ambos os arquivos crie uma pasta na raiz do projeto /data e insira ambos os arquivos .csv, nomeados como:

    ```sh
    # arquivo limpo de exportações
        dados_comex_EXP_2014_2024.csv
    # arquivo limpo de importações
        dados_comex_IMP_2014_2024.csv
    ```

8. Caso queira, você pode importar os dados da base do COMEX executando o seguinte comando:

    ```sh
    flask comex update
    # or
    flask comex update --help # para conhecer as opções
    ```

9. Caso queira importar somente um dos tipos de dados ('Importações' ou 'Exportações) execute estes comandos:

     ```sh
    flask comex update importacoes # para dados da importação
    # or
    flask comex update exportacoes # para dados da exportação
    ```

9. Execute o servidor Flask

    ```sh
    flask run
    ```

10.  Abra em um navegador: [http://localhost:5000](http://localhost:5000)

---

## Testes

A cada atualização é recomendado rodar todos os testes a fim de garantir o funcionamento do programa.

```sh
pytest
```

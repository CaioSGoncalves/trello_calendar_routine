# Auto Calendar

## Descrição
O Auto Calendar é um projeto que sincroniza os cards do Trello com eventos no Google Calendar. Ele permite criar eventos automaticamente para os cards que estão nas listas "A Fazer" e "Em andamento" do Trello.

## Requisitos
- Python 3.12 ou superior
- uv
- Conta no Google com acesso ao Google Calendar
- Conta no Trello

## Instalação

1. Instale as dependências:
   ```sh
   uv sync
   ```

2. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```properties
   TRELLO_API_KEY=your_trello_api_key
   TRELLO_TOKEN=your_trello_token
   TRELLO_BOARD_ID=your_trello_board_id
   GOOGLE_CALENDAR_ID=your_google_calendar_id
   ```

3. Adicione as credenciais do Google:
   Coloque o arquivo `credentials.json` na pasta `src`.

## Uso
Para rodar o script e criar eventos para hoje:
```sh
make run
```

Para rodar o script e criar eventos para a próxima segunda-feira:
```sh
make run-monday
```

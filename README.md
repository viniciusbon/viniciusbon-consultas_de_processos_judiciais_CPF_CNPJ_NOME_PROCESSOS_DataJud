Bot de Consulta Processual (DataJud) para Telegram
Este é um bot para Telegram desenvolvido para realizar consultas de processos judiciais diretamente na base de dados pública do DataJud, mantida pelo Conselho Nacional de Justiça (CNJ) do Brasil.

Desenvolvido por: Vinicius Mantovam

📖 Sobre o Projeto

O objetivo deste bot é facilitar o acesso a informações processuais de diversos tribunais brasileiros de forma rápida e automatizada através do Telegram. O usuário pode buscar por nome completo, CPF, CNPJ ou número do processo, e o bot retornará os resultados encontrados em formato de arquivo JSON.

✨ Funcionalidades Principais
Busca Multi-critério: Realiza buscas por:

Nome Completo da parte (polo ativo ou passivo).

CPF (com validação de formato).

CNPJ (com validação de formato, atualmente disponível apenas para o TST).

Número do Processo.

Consulta em Múltiplos Tribunais: O bot varre uma lista pré-definida de tribunais para encontrar os processos.

Validação de Dados: Inclui um validador para CPF e CNPJ para evitar buscas com dados inválidos.

Resultados: Os resultados são entregues como arquivos .json diretamente no chat, facilitando a análise e o armazenamento dos dados.

Interface Simples: Interação intuitiva através de comandos e botões no Telegram.

 <img src= "Telegram Web - Google Chrome.jpg" width="550" height="305" />

 <img src= "Telegram Web - Google Chrome.png" width="550" height="305" />


🛠️ Tecnologias Utilizadas
Linguagem: Python 3

Biblioteca para o Bot: python-telegram-bot

Requisições HTTP: requests

API: API Pública do DataJud (CNJ)

🚀 Como Configurar e Rodar o Projeto
Pré-requisitos
Python 3.8 ou superior

Conta no Telegram

1. Clone o Repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_SEU_REPOSITORIO>

2. Instale as Dependências
É recomendado criar um ambiente virtual:

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

Instale as bibliotecas necessárias:

pip install python-telegram-bot requests

3. Obtenha sua Chave de API do Telegram
Para que o bot funcione, você precisa de um token de acesso fornecido pelo Telegram.

Abra o Telegram e procure pelo bot @BotFather.

Inicie uma conversa com ele e envie o comando /newbot.

Siga as instruções para dar um nome e um nome de usuário (que deve terminar em bot) para o seu novo bot.

Ao final, o BotFather irá gerar um token de API. Copie este token.

Abra o arquivo de código Python e cole o token na seguinte variável:

TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"

4. Chave de API do DataJud
A chave pública para acesso à API do DataJud utilizada neste projeto foi obtida através da documentação oficial do serviço disponibilizado pelo CNJ. A chave está configurada na variável:

DATAJUD_API_KEY = "Chave da API"

Esta é uma chave de acesso público e pode ser alterada pelo CNJ a qualquer momento.

5. Execute o Bot
Com o token configurado, execute o script:

python main.py

Seu bot estará online e pronto para receber comandos no Telegram!

🤖 Como Usar o Bot
Encontre seu bot no Telegram pelo nome de usuário que você criou.

Envie o comando /start para ver a mensagem de boas-vindas.

Envie /buscar para iniciar uma nova consulta.

Selecione o tipo de busca desejada (Nome, CPF, CNPJ ou Nº do Processo).

Envie o termo que deseja pesquisar.

Aguarde o bot consultar os tribunais e enviar os resultados.

Para interromper uma operação, use o comando /cancelar.

🙏 Agradecimentos

O validador de CPF e CNPJ utilizado neste projeto foi adaptado do excelente trabalho disponível no repositório: eduardoranucci/validador-cnpj-cpf.
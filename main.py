import requests
import json
import re
import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# --- CONFIGURAÇÃO GERAL ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# COLOQUE SEU TOKEN AQUI!
TELEGRAM_BOT_TOKEN = "SUA_CHAVE_API"
DATAJUD_API_KEY = "SUA_CHAVE_API"

tribunais_validos = {
    "TST": "api_publica_tst", "TJSP": "api_publica_tjsp", "TJRJ": "api_publica_tjrj",
    "TJMG": "api_publica_tjmg", "TJRS": "api_publica_tjrs", "TJBA": "api_publica_tjba",
    "TJPR": "api_publica_tjpr", "TRF1": "api_publica_trf1", "TRF2": "api_publica_trf2",
    "TRF3": "api_publica_trf3", "TRF4": "api_publica_trf4", "TRF5": "api_publica_trf5",
    "STJ": "api_publica_stj", "STF": "api_publica_stf",
}

SELECTING_ACTION, GETTING_TERM = range(2)

# --- NOVAS FUNÇÕES DE VALIDAÇÃO ---

def is_cpf_valid(cpf: str) -> bool:
    """Valida um CPF. Retorna True se válido, False caso contrário."""
    cpf = re.sub(r'[^\d]', '', cpf) # Remove caracteres não numéricos

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Validação do primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito_1 = (soma * 10) % 11
    if digito_1 == 10:
        digito_1 = 0
    if digito_1 != int(cpf[9]):
        return False

    # Validação do segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito_2 = (soma * 10) % 11
    if digito_2 == 10:
        digito_2 = 0
    if digito_2 != int(cpf[10]):
        return False

    return True

def is_cnpj_valid(cnpj: str) -> bool:
    """Valida um CNPJ. Retorna True se válido, False caso contrário."""
    cnpj = re.sub(r'[^\d]', '', cnpj) # Remove caracteres não numéricos
    
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    # Validação do primeiro dígito
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos[i] for i in range(12))
    resto = soma % 11
    digito_1 = 0 if resto < 2 else 11 - resto
    if digito_1 != int(cnpj[12]):
        return False

    # Validação do segundo dígito
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos[i] for i in range(13))
    resto = soma % 11
    digito_2 = 0 if resto < 2 else 11 - resto
    if digito_2 != int(cnpj[13]):
        return False

    return True

# --- FUNÇÕES DO BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Olá, {user_name}!\n"
        f"Eu sou um bot para consultar processos no DataJud do CNJ.\n\n"
        f"Envie /buscar para começar uma nova consulta ou /cancelar para interromper uma operação."
    )

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Nome Completo", callback_data="nome")],
        [InlineKeyboardButton("CPF", callback_data="cpf")],
        [InlineKeyboardButton("CNPJ (Apenas TST)", callback_data="cnpj")],
        [InlineKeyboardButton("Nº do Processo", callback_data="processo")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Por favor, selecione o tipo de busca:", reply_markup=reply_markup)
    return SELECTING_ACTION

async def get_search_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    search_type = query.data
    context.user_data['search_type'] = search_type
    
    type_map = {
        'nome': 'o nome completo', 'cpf': 'o CPF',
        'cnpj': 'o CNPJ', 'processo': 'o número do processo'
    }
    await query.edit_message_text(text=f"Você selecionou: {query.data.upper()}\n\nAgora, por favor, envie {type_map[search_type]} para a busca.")
    return GETTING_TERM

async def execute_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    search_type = context.user_data.get('search_type')
    term = update.message.text
    
    if not search_type:
        await update.message.reply_text("Ocorreu um erro. Por favor, inicie uma nova busca com /buscar.")
        return ConversationHandler.END

    # --- INTEGRAÇÃO DA VALIDAÇÃO ---
    if search_type == 'cpf':
        if not is_cpf_valid(term):
            await update.message.reply_text("❌ CPF inválido. Por favor, verifique o número e tente novamente com /buscar.")
            context.user_data.clear()
            return ConversationHandler.END

    if search_type == 'cnpj':
        if not is_cnpj_valid(term):
            await update.message.reply_text("❌ CNPJ inválido. Por favor, verifique o número e tente novamente com /buscar.")
            context.user_data.clear()
            return ConversationHandler.END
    # --- FIM DA INTEGRAÇÃO DA VALIDAÇÃO ---

    await update.message.reply_text(f"Iniciando busca por {search_type.upper()}: '{term}'.\nIsso pode levar alguns minutos...")

    termo_busca = ""
    campos_busca = []

    if search_type == 'nome':
        termo_busca = re.sub(r"[^\w\s]", "", term, flags=re.UNICODE)
        campos_busca = ["poloAtivo.nome", "poloPassivo.nome"]
    elif search_type == 'cpf':
        termo_busca = re.sub(r'\D', '', term)
        campos_busca = ["poloAtivo.documento", "poloPassivo.documento"]
    elif search_type == 'cnpj':
        termo_busca = re.sub(r'\D', '', term)
        campos_busca = ["poloAtivo.cnpj", "poloPassivo.cnpj"]
    elif search_type == 'processo':
        termo_busca = re.sub(r"[^\d\w]", "", term)
        campos_busca = ["numeroProcesso"]

    query_data = {
        "size": 10,
        "query": {"multi_match": {"query": termo_busca, "fields": campos_busca, "type": "phrase"}}
    }
    
    headers = {'Authorization': f'APIKey {DATAJUD_API_KEY}', 'Content-Type': 'application/json'}

    for sigla, alias in tribunais_validos.items():
        if search_type == "cnpj" and sigla != "TST":
            continue

        url = f"https://api-publica.datajud.cnj.jus.br/{alias}/_search"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Consultando {sigla}...")
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(query_data), timeout=25)
            if response.status_code == 200:
                dados = response.json()
                total_resultados = dados.get('hits', {}).get('total', {}).get('value', 0)
                
                if total_resultados > 0:
                    status_message = f"✅ {total_resultados} resultado(s) encontrado(s) em {sigla}."
                    nome_arquivo = f"resultados_{search_type}_{termo_busca[:15]}_{sigla}.json"
                    with open(nome_arquivo, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)
                    
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=status_message)
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(nome_arquivo, 'rb'))
                    
                    os.remove(nome_arquivo)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Erro em {sigla}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Erro de conexão em {sigla}: {e}")

    await update.message.reply_text("Busca concluída em todos os tribunais!")
    await update.message.reply_text("Desenvolvida por Vinicius Mantovam.")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Busca cancelada. Envie /buscar para começar de novo.")
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    if TELEGRAM_BOT_TOKEN == "SEU_TOKEN_AQUI_DO_BOTFATHER":
        print("ERRO: Por favor, substitua 'SEU_TOKEN_AQUI_DO_BOTFATHER' pelo token do seu bot.")
        return
        
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("buscar", start_search)],
        states={
            SELECTING_ACTION: [CallbackQueryHandler(get_search_type)],
            GETTING_TERM: [MessageHandler(filters.TEXT & ~filters.COMMAND, execute_search)],
        },
        fallbacks=[CommandHandler("cancelar", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("Bot iniciado com validador de CPF/CNPJ. Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()
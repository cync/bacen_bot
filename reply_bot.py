import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from pydantic import BaseModel, Field
from storage import get_store
from bacen_feed import (
    get_ultimo_normativo, 
    get_normativos_hoje, 
    get_normativos_ontem, 
    get_normativos_semanal,
    format_normativo_message,
    format_multiple_normativos_message
)

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    TELEGRAM_TOKEN: str = Field(...)

def get_settings() -> Settings:
    return Settings(TELEGRAM_TOKEN=os.environ["TELEGRAM_TOKEN"])

s = get_settings()
bot = Bot(token=s.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
store = get_store()

@dp.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer("Olá! 👋\n\n<b>Comandos disponíveis:</b>\n• <b>oi</b> - Autorizar avisos automáticos\n• <b>/stop</b> - Cancelar avisos\n• <b>status</b> - Status do sistema\n• <b>ultimo</b> - Último normativo\n• <b>hoje</b> - Normativos de hoje\n• <b>ontem</b> - Normativos de ontem\n• <b>semanal</b> - Normativos desta semana")

@dp.message(Command("stop"))
async def on_stop(message: types.Message):
    store.remove_subscriber(message.chat.id)
    await message.answer("Você foi removido(a) da lista. ❌\nSe quiser voltar, mande <b>oi</b>.")

@dp.message(F.text.lower() == "oi")
async def on_oi(message: types.Message):
    user = message.from_user
    
    # Verifica se o usuário já está inscrito
    user_info = store.get_subscriber_info(message.chat.id)
    
    if user_info:
        # Usuário já está inscrito
        # Usa username se disponível, senão usa first_name, senão usa "usuário"
        display_name = user.username or user.first_name or "usuário"
        await message.answer(f"Olá @{display_name}, você já está cadastrado no Bacen_bot!")
    else:
        # Usuário não está inscrito, cadastra
        store.upsert_subscriber(
            chat_id=message.chat.id,
            first_name=user.first_name,
            username=user.username,
        )
        await message.answer("✅ Pronto! Você autorizou receber resumos de normativos do BACEN.\nPara sair, envie /stop.")

@dp.message(F.text.lower() == "ultimo")
async def on_ultimo(message: types.Message):
    """Retorna o último normativo publicado"""
    try:
        await message.answer("🔍 Buscando último normativo...")
        normativo = get_ultimo_normativo()
        
        if normativo:
            msg = format_normativo_message(normativo)
            await message.answer(msg)
        else:
            await message.answer("❌ Não foi possível encontrar o último normativo.")
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar último normativo: {str(e)}")

@dp.message(F.text.lower() == "hoje")
async def on_hoje(message: types.Message):
    """Retorna todos os normativos de hoje"""
    try:
        await message.answer("🔍 Buscando normativos de hoje...")
        normativos = get_normativos_hoje()
        
        msg = format_multiple_normativos_message(normativos, "Hoje")
        await message.answer(msg)
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar normativos de hoje: {str(e)}")

@dp.message(F.text.lower() == "ontem")
async def on_ontem(message: types.Message):
    """Retorna todos os normativos de ontem"""
    try:
        await message.answer("🔍 Buscando normativos de ontem...")
        normativos = get_normativos_ontem()
        
        msg = format_multiple_normativos_message(normativos, "Ontem")
        await message.answer(msg)
    except Exception as e:
        await message.answer(f"❌ Erro ao buscar normativos de ontem: {str(e)}")

@dp.message(F.text.lower() == "status")
async def on_status(message: types.Message):
    """Mostra o status do sistema e inscrições"""
    try:
        await message.answer("🔍 Verificando status do sistema...")
        
        # Verifica saúde do banco
        health = store.health_check()
        
        if health['status'] == 'healthy':
            subscriber_count = health['subscriber_count']
            seen_items_count = health['seen_items_count']
            
            # Verifica se o usuário está inscrito
            user_info = store.get_subscriber_info(message.chat.id)
            
            status_msg = f"📊 <b>Status do Sistema BACEN Bot</b>\n\n"
            status_msg += f"✅ <b>Banco de dados:</b> Saudável\n"
            status_msg += f"👥 <b>Total de inscritos:</b> {subscriber_count}\n"
            status_msg += f"📄 <b>Normativos processados:</b> {seen_items_count}\n\n"
            
            if user_info:
                joined_date = user_info['joined_at'].strftime("%d/%m/%Y %H:%M")
                status_msg += f"✅ <b>Seu status:</b> Inscrito\n"
                status_msg += f"📅 <b>Inscrito desde:</b> {joined_date}\n"
                status_msg += f"🔔 <b>Notificações:</b> Ativas"
            else:
                status_msg += f"❌ <b>Seu status:</b> Não inscrito\n"
                status_msg += f"💡 <b>Para receber notificações:</b> Envie 'oi'"
            
            await message.answer(status_msg)
        else:
            await message.answer(f"❌ Problema no sistema: {health.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        await message.answer(f"❌ Erro ao verificar status: {str(e)}")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Não entendi 🤖 — Comandos disponíveis:\n• <b>oi</b> - Autorizar avisos\n• <b>/stop</b> - Cancelar avisos\n• <b>status</b> - Status do sistema\n• <b>ultimo</b> - Último normativo\n• <b>hoje</b> - Normativos de hoje\n• <b>ontem</b> - Normativos de ontem\n• <b>semanal</b> - Normativos desta semana")

async def main():
    print("reply_bot: ouvindo mensagens...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

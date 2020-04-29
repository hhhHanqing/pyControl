from telegram.ext import Updater
from telegram import Bot,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove
rigBot = Bot(token='1059352567:AAHXJyteP1gxDPgA3vSeRSBlQ0iVMsC38uI')
updater = Updater(token='1059352567:AAHXJyteP1gxDPgA3vSeRSBlQ0iVMsC38uI', use_context=True)
dispatcher = updater.dispatcher

def telegram_notify(message):
    rigBot.send_message(chat_id=1095148293,text=message)
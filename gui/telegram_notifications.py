from telegram.ext import Updater
from telegram import Bot,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackQueryHandler

class Telegram():
    def __init__(self):
        self.rigBot = Bot(token='1059352567:AAHXJyteP1gxDPgA3vSeRSBlQ0iVMsC38uI')
        self.updater = Updater(token='1059352567:AAHXJyteP1gxDPgA3vSeRSBlQ0iVMsC38uI', use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.btn_msg_id = None

    def notify(self,message):
        self.rigBot.send_message(chat_id=1095148293,text=message, parse_mode='HTML')

    def send_button(self,message,reply_markup,callback_fxn):
        btn_id = self.rigBot.send_message(chat_id=1095148293, text=message, reply_markup=reply_markup)
        menu_handler = CallbackQueryHandler(callback_fxn)
        self.dispatcher.add_handler(menu_handler)
        self.updater.start_polling()
        return btn_id['message_id']

    def close(self):
        self.rigBot.delete_message(chat_id=1095148293, message_id=self.btn_msg_id)
    
    def delete(self):
        self.updater.stop()
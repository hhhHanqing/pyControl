from telegram.ext import Updater
from telegram import Bot,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackQueryHandler

class Telegram():
    def __init__(self,subjectboxes):
        self.subjectboxes = subjectboxes
        self.rigBot = Bot(token='1059352567:AAHXJyteP1gxDPgA3vSeRSBlQ0iVMsC38uI')
        self.updater = Updater(token='1059352567:AAHXJyteP1gxDPgA3vSeRSBlQ0iVMsC38uI', use_context=True)
        self.dispatcher = self.updater.dispatcher
        menu_handler = CallbackQueryHandler(self.callback)
        self.dispatcher.add_handler(menu_handler)
        self.updater.start_polling()

    def notify(self,message):
        self.rigBot.send_message(chat_id=1095148293,text=message, parse_mode='HTML')

    def send_button(self,message,reply_markup):
        btn_id = self.rigBot.send_message(chat_id=1095148293, text=message, reply_markup=reply_markup)
        return btn_id['message_id']

    def remove_button(self,btn_msg_id):
        self.rigBot.delete_message(chat_id=1095148293, message_id=btn_msg_id)
    
    def callback(self,update,context):
        rig = self.subjectboxes[int(update.callback_query.data)]
        rig.board.get_variable('trial_current_number___')
        self.rigBot.answer_callback_query(update.callback_query.id) # send answer so the button doesn't keep on spinning.
        msg = "<u><b>{}</b></u>\nSession duration = {}\nCurrent trial = {}".format(
            rig.boxTitle.text(),
            rig.time_text.text(),
            eval(str(rig.board.sm_info['variables']['trial_current_number___']))
            )
        self.notify(msg)
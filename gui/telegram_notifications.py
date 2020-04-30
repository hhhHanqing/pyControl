from telegram.ext import Updater
from telegram import Bot,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackQueryHandler

class Telegram():
    def __init__(self,subjectboxes,token,chatID):
        self.subjectboxes = subjectboxes
        self.rigBot = Bot(token=token)
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.chat_id = chatID
        menu_handler = CallbackQueryHandler(self.callback)
        self.dispatcher.add_handler(menu_handler)
        self.updater.start_polling()

    def notify(self,message):
        self.last_notification = self.rigBot.send_message(chat_id=self.chat_id,text=message, parse_mode='HTML')

    def send_button(self,message,reply_markup):
        btn_id = self.rigBot.send_message(chat_id=self.chat_id, text=message, reply_markup=reply_markup)
        return btn_id['message_id']

    def remove_msg(self,btn_msg_id):
        self.rigBot.delete_message(chat_id=self.chat_id, message_id=btn_msg_id)
    
    def callback(self,update,context):
        rig = self.subjectboxes[int(update.callback_query.data)]
        rig.board.get_variable('trial_current_number___')
        self.rigBot.answer_callback_query(update.callback_query.id) # send answer so the button doesn't keep on spinning.
        msg = "<u><b>{}</b></u>\n\nClock = {}\nCurrent trial = {}".format(
            rig.boxTitle.text(),
            rig.time_text.text(),
            eval(str(rig.board.sm_info['variables']['trial_current_number___']))
            )
        self.notify(msg)
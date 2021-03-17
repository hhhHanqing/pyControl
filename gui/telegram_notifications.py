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
        self.active_rigs_dict = {}
        self.button_menu_msg_id = None

    def notify(self,message):
        self.last_notification = self.rigBot.send_message(chat_id=self.chat_id,text=message, parse_mode='HTML')

    def add_button(self,boxNum,boxTitle):
        self.active_rigs_dict[str(boxNum)] = InlineKeyboardButton(boxTitle.text(), callback_data= boxNum)
        self.update_button_menu()

    def remove_button(self,boxNum):
        del self.active_rigs_dict[str(boxNum)]
        self.update_button_menu()

    def update_button_menu(self):
        button_list = []
        for box_btn in sorted(self.active_rigs_dict.keys()):
            button_list.append([self.active_rigs_dict[box_btn]])

        button_markup = InlineKeyboardMarkup(button_list)

        if self.button_menu_msg_id:
            self.remove_msg(self.button_menu_msg_id)

        if self.active_rigs_dict:
            title = "Click rig button below to get animal specific updates"
            btn_id = self.rigBot.send_message(chat_id=self.chat_id, text=title, reply_markup=button_markup)
            self.button_menu_msg_id = btn_id['message_id']

    def remove_msg(self,btn_msg_id):
        self.rigBot.delete_message(chat_id=self.chat_id, message_id=btn_msg_id)
    
    def callback(self,update,context):
        rig = self.subjectboxes[int(update.callback_query.data)]
        rig.board.get_variable('trial_current_number___')
        rig.board.get_variable('completed_sequences___')
        self.rigBot.answer_callback_query(update.callback_query.id) # send answer so the button doesn't keep on spinning.
        completedTrials = eval(str(rig.board.sm_info['variables']['trial_current_number___'])) - 1
        completedSeq = eval(str(rig.board.sm_info['variables']['completed_sequences___']))
        if completedTrials > 0:
            msg = \
                f"<u><b>{rig.boxTitle.text()}</b></u>\n\n" \
                f"⏱️ Time = {rig.time_text.text()}\n" \
                f"✅ Correct = {round(completedSeq/completedTrials*100,2)}% ({completedSeq}/{completedTrials})"
        else:
            msg = \
                f"<u><b>{rig.boxTitle.text()}</b></u>\n\n" \
                f"⏱️ Time = {rig.time_text.text()}\n" \
                f"✅ Correct = There haven't been any completed trials yet"
        self.notify(msg)
from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import time 
import logging
import codecs
import csv
from config import TOKEN
 
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger(__name__)
 
PHOTO, CHOOSING = range(2)

def make_keyboard(columns):
    i = 0
    reply_keyboard = []
    tmp_keyboard=[]
    with codecs.open('recycle_db.csv', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        i=0
        for row in reader:
            if row[1] != 'item':
                i+=1
                tmp_keyboard.append(row[1])
                if i >= columns:
                    reply_keyboard.append(tmp_keyboard)
                    tmp_keyboard = []
                    i=0
    reply_keyboard.append(['cancel'])
    return reply_keyboard
  
 
def start(bot, update):
    reply_keyboard = make_keyboard(2)
    update.message.reply_text(
        'Выбирите категорию отходов и загрузите фотографию.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
 
    return CHOOSING

def custom_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    return PHOTO
 
def photo(bot, update, user_data):
    update.message.reply_text('update')
    text = user_data['choice']
    #print (update.to_json())
    #print (bot.to_json())
    #updates = bot.getUpdates()
    #print([u.message.text for u in updates])
    user = update.message.from_user
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    file_name = "files/{}-{}-{}.jpg".format(user.id,text,time.time())
    photo_file.download(file_name)
    logger.info("Photo of %s: %s" % (user.first_name, file_name))
    update.message.reply_text('Превосходно! Спасибо за предоставленное изображение!')
    reply_keyboard = make_keyboard(2)
    update.message.reply_text('Выбирите категорию отходов и загрузите фотографию.',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSING
 
 
def skip_photo(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a photo." % user.first_name)
    update.message.reply_text('Фотография не была загружена. Попробуйте заново выбрать категорию отходов.')
 
    return ConversationHandler.END
 
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Благодарим за помощь! Надеемся на дальнейшее сотрудничество.')
 
    return ConversationHandler.END

def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']
 
    update.message.reply_text("I learned these facts about you:"
                              "%s"
                              "Until next time!" % facts_to_str(user_data))
 
    user_data.clear()
    return ConversationHandler.END
 
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
 
 
def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)
 
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
 
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
 
        states={
            CHOOSING : [RegexHandler('^(.*?)$',
                                    custom_choice,
                                    pass_user_data=True)],
            PHOTO: [MessageHandler(Filters.photo, photo,pass_user_data = True),
                    CommandHandler('skip', skip_photo)]
            },
 
        fallbacks=[CommandHandler('cancel', cancel)]
    )
 
    dp.add_handler(conv_handler)
 
    # log all errors
    dp.add_error_handler(error)
 
    # Start the Bot
    updater.start_polling()
 
    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
 
 
if __name__ == '__main__':
    main()

import logging
import ephem
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

def greet_user(update, context):
    print("Вызван /start")
    name = update.message.from_user.first_name
    update.message.reply_text("Дратути, " + name + "!")

def talk_to_me(update, context):
    text = update.message.text
    print('повторялка')
    print(text)
    if (text == "Дурак") or (text == "дурак"):
        update.message.reply_text("Сам дурак")
    else:
        update.message.reply_text(text)

def constellation(update, context):
    try:
        text = update.message.text.split()[1].lower()
        print('планета')
        print(text)
        day = datetime.date.today()
        if text == 'mars':
            mars = ephem.Mars(day)
            constellation = ephem.constellation(mars)
            update.message.reply_text(f'Mars is currently in the constellation of {constellation[1]}.')    
        elif text == 'mercury':
            mercury = ephem.Mercury(day)
            constellation = ephem.constellation(mercury)
            update.message.reply_text(f'Mercury is currently in the constellation of {constellation[1]}.')
        elif text == 'venus':
            venus = ephem.Venus(day)
            constellation = ephem.constellation(venus)
            update.message.reply_text(f'Venus is currently in the constellation of {constellation[1]}.')
        elif text == 'earth':
            update.message.reply_text('The constellation of Earth is relative to the observer.')
        elif text == 'jupiter':
            jupiter = ephem.Jupiter(day)
            constellation = ephem.constellation(jupiter)
            update.message.reply_text(f'Jupiter is currently in the constellation of {constellation[1]}.')
        elif text == 'saturn':
            saturn = ephem.Saturn(day)
            constellation = ephem.constellation(saturn)
            update.message.reply_text(f'Saturn is currently in the constellation of {constellation[1]}.')
        elif text == 'uranus':
            uranus = ephem.Uranus(day)
            constellation = ephem.constellation(uranus)
            update.message.reply_text(f'Uranus is currently in the constellation of {constellation[1]}.')
        elif text == 'neptune':
            neptune = ephem.Neptune(day)
            constellation = ephem.constellation(neptune)
            update.message.reply_text(f'Neptune is currently in the constellation of {constellation[1]}.')
        else:
            update.message.reply_text(f'There is no such planet.')
    except IndexError:
        update.message.reply_text('You did not enter the name of the planet.')
    

def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet",constellation))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    dp.add_handler(MessageHandler(Filters.text, constellation))

    logging.info("Bot has started")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
import logging
import ephem
import re
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

PROXY = {'proxy_url': settings.PROXY_URL,
    'urllib3_proxy_kwargs': {'username': settings.PROXY_USERNAME, 'password': settings.PROXY_PASSWORD}}

def greet_user(update, context):
    print("Вызван /start")
    name = update.message.from_user.first_name
    update.message.reply_text("Hello, " + name + "!")

def talk_to_me(update, context):
    text = update.message.text.lower()
    print('повторялка')
    print(text)
    if text == "fool":
        update.message.reply_text("You're fool!")
    else:
        update.message.reply_text(text)

def planet(update, context):
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
    
def count(update, context):
    text = update.message.text.split()
    print('количество слов')
    print(text)
    text.remove('/wordcount')
    new_text = []
    for word in text:
        word = re.sub(r'[^a-zA-Z ]+', '', word)
        if word:
            new_text.append(word)
    if len(new_text) == 0:
        update.message.reply_text('You did not enter any word.')
    elif len(new_text) == 1:
        update.message.reply_text(f'You entered 1 word.')
    else:
        update.message.reply_text(f'You entered {len(new_text)} words.')
    

def full_moon(update, context):
    try:
        text = update.message.text.split()[1]
        print("полнолуние")
        try:
            date = datetime.strptime(text, "%Y/%m/%d")
            update.message.reply_text(ephem.next_full_moon(date))
        except ValueError:
            try:
                date = datetime.strptime(text, "%Y-%m-%d")
                update.message.reply_text(ephem.next_full_moon(date))
            except ValueError:
                update.message.reply_text('Incorrect data format. Should be yyyy/mm/dd or yyyy-mm-dd.')
    except IndexError:
        update.message.reply_text('You did not enter a date.')

def played(user_data):
    if 'cities_used' not in user_data:
        user_data['cities_used'] = []
    return user_data['cities_used']

def my_city_base(user_data):
    if 'my_cities' not in user_data:
        user_data['my_cities'] = []
        with open('cities.txt', 'r', encoding='utf-8') as cities:
            for line in cities:
                user_data['my_cities'].append(line.replace('\n',''))
    return user_data['my_cities']

def last_city_used(user_data):
    if 'last_answer' not in user_data:
        user_data['last_answer'] = ''
    return user_data['last_answer']

def is_in_english(update, context, city):
    city = city.replace(' ', '')
    result = True
    for letter in city:
        if not bool(re.search('[-a-zA-Z]', letter)):
            update.message.reply_text('It should be in English.')
            result = False
            break
    return result

def refresh_data(context, user_city, my_answer):
    context.user_data['last_answer'] = my_answer #remember my answer
    context.user_data['cities_used'].append(user_city) # add user's city to used cities base
    context.user_data['cities_used'].append(my_answer) # add my answer to used cities base
    context.user_data['my_cities'].remove(my_answer) # delete my answer from base
    delete_from_my_base(context, user_city) # delete user's city from my base

def delete_from_my_base(context, user_city):
    for city in context.user_data['my_cities']:
        if city.lower().replace(' ','') == user_city.lower().replace(' ',''):
            context.user_data['my_cities'].remove(city)
            break

def give_my_answer(update, context, user_city):
    my_answer = ''
    for city in context.user_data['my_cities']:
        if user_city.lower()[-1] == city.lower()[0]:
            my_answer = city
            update.message.reply_text(f'{my_answer}, your turn.') # print my answer
            refresh_data(context, user_city, my_answer)
            break
    if not my_answer: # if I don't have an answer
        update.message.reply_text('Congratulations! You won!')
        delete_data(context) # delete all used cities from base, refresh my city base        

def already_used(update, context, entered_city):
    is_used = False
    for city in context.user_data['cities_used']:
        if city.lower().replace(' ','') == entered_city.lower().replace(' ',''):
            is_used = True
            update.message.reply_text(
f'''This city was already used in the game.
If you surrender, enter: I surrender.
'''
) 
            break
    return is_used

def delete_data(context):
    context.user_data['cities_used'] = []   # delete all cities from used
    context.user_data['my_cities'] = []     # delete all citied from my base
    context.user_data['last_answer'] = ''   # delete my last answer
    with open('cities.txt', 'r', encoding='utf-8') as cities: # refresh my city base
        for line in cities:
            context.user_data['my_cities'].append(line.replace('\n',''))

def surrender_cheking(update, context, user_text):
    if user_text.lower().replace(' ','') == 'isurrender':
        update.message.reply_text('I won!')
        delete_data(context)
        return True
    else:
        return False


def rules_are_satisfied(update, context, user_text):
    my_city = context.user_data['last_answer'] # if I didn't answer before it's empty
    if not already_used(update, context, user_text):
        if my_city: # if I answered before I check rules
            if user_text.lower()[0] == my_city.lower()[-1]:
                return True
            else:
                update.message.reply_text(
f'''You should enter a city starting with {my_city.upper()[-1]}.
If you surrender, enter: I surrender.
'''
)
                return False # rules are not met
        else:
            return True # if I didn't answer before I don't check rules
    else:
        return False # if city was used before

def cities_game(update, context):
    text = update.message.text.replace('/cities','').strip()
    print("города")
    print(text)
    context.user_data['cities_used'] = played(context.user_data)    # already used citied
    context.user_data['my_cities'] = my_city_base(context.user_data)    # my city base
    context.user_data['last_answer'] = last_city_used(context.user_data)    # last answer
    
    try:
        if is_in_english(update, context, text):
            if not surrender_cheking(update, context, text): # check if user surrender
                if rules_are_satisfied(update, context, text): 
                    give_my_answer(update, context, text)
    except IndexError:
        update.message.reply_text('You did not enter a city.')    

def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", planet))
    dp.add_handler(CommandHandler("wordcount", count))
    dp.add_handler(CommandHandler("next_full_moon", full_moon))
    dp.add_handler(CommandHandler("cities", cities_game))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info("Bot has started")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
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
    update.message.reply_text("Дратути, " + name + "!")

def talk_to_me(update, context):
    text = update.message.text.lower()
    print('повторялка')
    print(text)
    if text == "дурак":
        update.message.reply_text("Сам дурак")
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


def cities_game(update, context):

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

    def is_in_russian(city):
        city = city.replace(' ', '')
        result = True
        for letter in city:
            if not bool(re.search('[-а-яА-Я]', letter)):
                result = False
                break
        return result

    def last_letter(city):
        city = city.lower().replace(' ', '')
        for letter in reversed(city):
            if letter != "ь" and letter != "ъ" and letter != "ы" and letter != "ё":
                return(letter)
            
    def answer(entered_city):
        for city in context.user_data['my_cities']:
            if city.lower()[0] == last_letter(entered_city):
                context.user_data['last_answer'] = city
                break
            else:
                context.user_data['last_answer'] = ''
        if context.user_data['last_answer']:
            check_my_base(entered_city)                                                         #если введенный пользоватедем город есть в моей базе, удаляю его
            context.user_data['my_cities'].remove(context.user_data['last_answer'])             #удаляю свой ответ из моей базы
            context.user_data['cities_used'].append(entered_city)                               #добавляю введенный пользователем город в список использованных
            context.user_data['cities_used'].append(context.user_data['last_answer'])           #добавляю свой ответ в список использованных
            update.message.reply_text(f'{context.user_data["last_answer"]}. Ваш ход.')          #вывожу свой ответ
        else:
            update.message.reply_text('Поздравляю. Вы выйграли!')                               #ответа нет
            delete_data()                                           

    def check_my_base(entered_city):
        for city in context.user_data['my_cities']:
            if city.lower().replace(' ','') == entered_city.lower().replace(' ',''):
                context.user_data['my_cities'].remove(city)
                break

    def already_used(entered_city):
        is_used = False
        for city in context.user_data['cities_used']:
            if city.lower().replace(' ','') == entered_city.lower().replace(' ',''):
                is_used = True
                break
        return is_used

    def delete_data():
        context.user_data['cities_used'] = []   #удаляем список исрользованных городов
        context.user_data['my_cities'] = []     #заново заполняем базу своих городов
        context.user_data['last_answer'] = ''
        with open('cities.txt', 'r', encoding='utf-8') as cities:
            for line in cities:
                context.user_data['my_cities'].append(line.replace('\n',''))

    text = update.message.text.replace('/cities','').strip()
    print("города")
    print(text)

    if text:
        if text.lower().replace(' ','') != 'ясдаюсь':
            context.user_data['cities_used'] = played(context.user_data)    #использованные города
            context.user_data['my_cities'] = my_city_base(context.user_data)    #база моих городов
            context.user_data['last_answer'] = last_city_used(context.user_data)    #последний ответ
            
            if is_in_russian(text):                                                                         #введенный город на русском
                if context.user_data['last_answer']:                                                        #отвечал ли я ранее
                    if last_letter(context.user_data['last_answer']) == text.lower()[0]:                    #проверяю введеный город
                        if already_used(text):                                                              #проверяю использовался ли ранее город
                            update.message.reply_text('''Этот город уже использовали в игре.
Если Вы сдаётесь, введите: Я сдаюсь.''')
                        else:
                            answer(text)
                    else:
                        update.message.reply_text(f'''Вы должны ввести город на букву {last_letter(context.user_data["last_answer"]).upper()}.
Если Вы сдаётесь, введите: Я сдаюсь.''')                
                else:
                    answer(text)                                                                      
            else:
                update.message.reply_text('Название города должно быть на русском языке.')
        else:
            update.message.reply_text('Я победил!')
            delete_data()
    else:
        update.message.reply_text('Вы не ввели город.')    

def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", planet))
    dp.add_handler(CommandHandler("wordcount", count))
    dp.add_handler(CommandHandler("next_full_moon", full_moon))
    dp.add_handler(CommandHandler("cities", cities_game))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    dp.add_handler(MessageHandler(Filters.text, planet))
    dp.add_handler(MessageHandler(Filters.text, count))
    dp.add_handler(MessageHandler(Filters.text, full_moon))
    dp.add_handler(MessageHandler(Filters.text, cities_game))

    logging.info("Bot has started")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
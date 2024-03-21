import datetime
import telebot
import re
import random
import schedule
import threading
import json
import time
from glob import glob
from settings import api
from apscheduler.schedulers.blocking import BlockingScheduler

bot = telebot.TeleBot(api)

compliments = []
with open('text_files/compliments.txt', 'r', encoding='utf-8') as f:
    for x in f:
        compliments.append(x[:-2])

wishes_morning = []
with open('text_files/wishes.txt', 'r', encoding='utf-8') as f:
    for x in f:
        wishes_morning.append(x[:-2])

wishes_night = []
with open('text_files/wishes_night.txt', 'r', encoding='utf-8') as f:
    for x in f:
        wishes_night.append(x[:-2])

anecdots = []
with open('text_files/anecdots.txt', 'r', encoding='utf-8') as f:
    for x in f:
        anecdots.append(x)

food = []
with open('text_files/food.txt', 'r', encoding='utf-8') as f:
    for x in f:
        food.append(x)

emoji_morning = ['💌', '💘', '💝', '💖', '💗', '💓', '💞', '💕', '❣', '🧡', '💛', '💚', '💙', '💜', '🤎', '🖤', '🤍', '🫶', '🐱', '🐇',
                 '🐰', '🐞']
emoji_night = ['💌', '💘', '💝', '💖', '💗', '💓', '💞', '💕', '❣', '🧡', '💛', '💚', '💙', '💜', '🤎', '♥', '🤍', '🌌', '🐱', '🌛', '🌆',
               '💤', '🐾']
help_text = "Инструкция по использованию МиниЭль(つ✧ω✧)つ\n" \
            "/help - инструкция по работе с ботом\n" \
            "/compliment - отправка комплимента ботом\n" \
            "/acquaintance - настройка бота для личного использования, при повторном вызове команды сохраняются только новые и корректные данные!\n" \
            "/meme - отправка мема/анекдота ботом\n" \
            "/yummy - на случай, когда не знаешь, что съесть💙\n" \
            "p.s. разработчик не видит Вашу переписку с ботом, для связи используйте ЛС с разработчиком"


def add_to_json(json_data):
    flag = 1
    data = json.load(open("users_data.json", encoding="utf-8"))
    if check_data(json_data):
        print("New user/update: " + json_data['username'])
        for i in range(len(data)):
            x = data[i]
            if x['chat_id'] == json_data['chat_id']:
                data[i]['name'] = json_data['name']
                data[i]['wake_up_time'] = datetime.datetime.strftime(
                    datetime.datetime.strptime(json_data['wake_up_time'], "%H:%M") - datetime.timedelta(hours=3),
                    "%H:%M")
                data[i]['sleep_time'] = datetime.datetime.strftime(
                    datetime.datetime.strptime(json_data['sleep_time'], "%H:%M") - datetime.timedelta(hours=3), "%H:%M")
                flag = 0
        if flag:
            json_data['wake_up_time'] = datetime.datetime.strftime(
                datetime.datetime.strptime(json_data['wake_up_time'], "%H:%M") - datetime.timedelta(hours=3), "%H:%M")
            json_data['sleep_time'] = datetime.datetime.strftime(
                datetime.datetime.strptime(json_data['sleep_time'], "%H:%M") - datetime.timedelta(hours=3), "%H:%M")
            data.append(json_data)
    with open("users_data.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def wake_up_step(message, user_info):
    user_info['name'] = message.text
    msg = bot.send_message(message.chat.id,
                           'Во сколько ты обычно встаешь? Укажи время в формате XX:XX по мск, чтобы я могла запомнить')
    bot.register_next_step_handler(msg, sleep_step, user_info)


def sleep_step(message, user_info):
    user_info['wake_up_time'] = message.text
    msg = bot.send_message(message.chat.id,
                           'Во сколько ты обычно ложишься спать? Укажи время в формате XX:XX по мск, чтобы я могла запомнить')
    bot.register_next_step_handler(msg, fix_step, user_info)


def fix_step(message, user_info):
    user_info['sleep_time'] = message.text
    bot.send_message(message.chat.id,
                     'Ура! ' + user_info['name'] + ', твои данные записаны(*¯︶¯*)')
    user_info['username'] = bot.get_chat_member(user_info['chat_id'], user_info['chat_id']).user.username
    add_to_json(user_info)


def good_morning_message(chat_id):
    text = "Доброе утро" + emoji_morning[random.randint(0, len(emoji_morning) - 1)] + '\n' + wishes_morning[
        random.randint(0, len(emoji_morning) - 1)] + \
           emoji_morning[random.randint(0, len(emoji_morning) - 1)]
    image_list = glob('good_morning_photos/*')
    pic = random.choice(image_list)
    bot.send_message(chat_id, text)
    bot.send_photo(chat_id, photo=open(pic, 'rb'))
    return 1


def good_night_message(chat_id):
    text = "Спокойной ночи" + emoji_night[random.randint(0, len(emoji_morning) - 1)] + '\n' + wishes_night[
        random.randint(0, len(emoji_morning) - 1)] + \
           emoji_night[random.randint(0, len(emoji_morning) - 1)]
    image_list = glob('good_night_photos/*')
    pic = random.choice(image_list)
    bot.send_message(chat_id, text)
    bot.send_photo(chat_id, photo=open(pic, 'rb'))

    return 1

def yummy(chat_id):
    text = food[random.randint(0, len(food) - 1)][:-1]+"?"
    bot.send_message(chat_id, text)
    return 1

def meme_message(chat_id):
    image_list = glob('memes/*')
    pic = random.choice(image_list)
    bot.send_photo(chat_id, photo=open(pic, 'rb'))
    return 1

def love_message(chat_id):
    image_list = glob('love_message_photos/*')
    pic = random.choice(image_list)
    bot.send_photo(chat_id, photo=open(pic, 'rb'))
    return 1

def check_data(data):
    gm = data['wake_up_time']
    gn = data['sleep_time']
    pattern = pattern = r'^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    if re.fullmatch(pattern, gm) and re.fullmatch(pattern, gn):
        return 1
    return 0


def acquaintance(chat_id):
    user_info = {}
    user_info['chat_id'] = chat_id
    msg = bot.send_message(chat_id, 'Как я могу к тебе обращаться?(* ^ ω ^)')
    bot.register_next_step_handler(msg, wake_up_step, user_info)


def job():
    time = datetime.datetime.now()
    current_time = time.strftime("%H:%M")
    data = json.load(open("users_data.json"))
    for x in data:
        if current_time == x['wake_up_time']:
            good_morning_message(x['chat_id'])
        if current_time == x['sleep_time']:
            good_night_message(x['chat_id'])


@bot.message_handler(commands=['start', 'help', 'compliment', 'acquaintance', 'meme', 'yummy'])
def get_command_messages(message):
    if message.text == "/start":
        bot.send_message(message.chat.id,
                         f"Нихао, {message.from_user.first_name}, рада видеть тебя\(★ω★)/" + '\n' + "для получения информации об использовании бота воспользуйся командой /help")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, help_text)
    elif message.text == '/compliment':
        x = random.randint(0, 10000)
        if x % 2 == 0:
            bot.send_message(message.from_user.id, compliments[random.randint(0, len(compliments) - 1)])
        else:
            love_message(message.from_user.id)
    elif message.text == '/acquaintance':
        acquaintance(message.from_user.id)
    elif message.text == '/meme':
        x = random.randint(0, 100)
        if x % 2 == 0:
            bot.send_message(message.from_user.id, anecdots[random.randint(0, len(anecdots) - 1)])
        else:
            meme_message(message.from_user.id)
    elif message.text == '/yummy':
        yummy(message.from_user.id)
    else:
        bot.send_message(message.from_user.id,
                         "Я пока не знаю такой команды, но ты можешь предложить обновление разработчику|･ω･)")


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id,
                         'привет! Чтобы узнать, как взаимодействовать с ботом, воспользуйся командой /help')
    elif 'грустно' in message.text.lower():
        bot.send_message(message.chat.id,
                         "нам всем порой бывает грустно, у тебя все получится!")
    elif 'скучаю' in message.text.lower():
        bot.send_message(message.chat.id,
                         "все проходит. пройдет и это")
    elif "спасибо" in message.text.lower():
        bot.send_message(message.chat.id,
                         "всегда пожалуйста! хорошего тебе дня)")
    else:
        bot.send_message(message.chat.id,
                         "Я пока не знаю такой команды, но ты можешь предложить обновление разработчику|･ω･)")


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


proc_bot = threading.Thread(target=bot.infinity_polling)
proc_bot.start()

scheduler = BlockingScheduler()
scheduler.add_job(job, 'interval', minutes=1)
scheduler.start()

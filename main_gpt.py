import telebot
from openai import OpenAI

bot = telebot.TeleBot('bot_token')
client = OpenAI(api_key='open_aitoken')

user_history = {}

def keyboard():
    markup = telebot.types.ReplyKeyboardMarkup()
    but_1 = telebot.types.KeyboardButton('Новый запрос')
    markup.add(but_1)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_history[user_id] = [{"role": "system", "content": "Ты полезный ассистент."}]

    bot.send_message(message.chat.id,
   "Привет! Я бот с ChatGPT. Задай мне вопрос!\n"
        "Используй /help для справки или 'Новый запрос' чтобы очистить историю.", reply_markup=keyboard())

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
   "Просто напиши мне сообщение - я отвечу с помощью ChatGPT!\n"
        "Команды:\n"
        "/start - начать новый диалог\n"
        "/help - эта справка\n"
        "'Новый запрос' - очистить историю", reply_markup=keyboard())

@bot.message_handler(func=lambda message: message.text == "Новый запрос")
def new_request(message):
    user_id = message.from_user.id

    user_history[user_id] = [
        {"role": "system", "content": "Ты полезный ассистент."}
    ]
    bot.send_message(
        message.chat.id,
   "История очищена! Задай новый вопрос."
        ,reply_markup=keyboard())

@bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.from_user.id

    if user_id not in user_history:
        user_history[user_id] = [{"role": "system", "content": "Ты полезный ассистент."}]

    user_history[user_id].append({"role": "user", "content": message.text})

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_history[user_id],
            max_tokens = 500
        )

        answer = response.choices[0].message.content

        user_history[user_id].append({"role": "assistant", "content": answer})

        bot.send_message(
            message.chat.id,
            answer,
            reply_markup=keyboard()
        )

    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}",
            reply_markup=keyboard()
        )


bot.infinity_polling()
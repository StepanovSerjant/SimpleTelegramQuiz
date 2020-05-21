from flask import Flask
from flask_sslify import SSLify
from flask import request
from flask import jsonify

import requests

from config import URL, TOKEN
from service import Player, write_client_json
from quiz_settings import check_last_answers, questions, quiz_start, quiz_restart, quiz_results, quiz_info


app = Flask(__name__)
sslify = SSLify(app)


def check_private_message(request):
    if 'message' in request and request['message']['chat']['type'] == 'private':
        return True


def check_callback_query_message(request):
    if 'callback_query' in request:
        return True


# базовая функция ответа пользователю
def answer_to_client(**kwargs):
    answer = {
        'method': 'sendMessage',
        'chat_id': '',
        'text': '',
    }

    for k, v in kwargs.items():
        answer[k] = v

    r = requests.post(URL, json=answer)
    return r.json()


def make_keyboard(question_id):

    buttons = []
    for variable in questions[question_id]['variables']:
        button = [{
            'text': variable,
            'callback_data': variable
        }]
        buttons.append(button)

    inline_keyboard = {'inline_keyboard': buttons}

    return inline_keyboard


ROUTE = '/{}'.format(TOKEN)

@app.route(ROUTE, methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        write_client_json(r)

        if check_callback_query_message(r):
            chat_id = r['callback_query']['message']['chat']['id']
            callback = r['callback_query']['data']
            current_player = Player(chat_id)

            if len(current_player.get_answers()) == 0:
                current_player.get_question_id(add=1)
                current_player.get_answers(add=callback)
                reply_markup = make_keyboard(current_player.get_question_id())
                answer_to_client(chat_id=chat_id, text=questions[current_player.get_question_id()]['question'], reply_markup=reply_markup)

            elif len(current_player.get_answers()) == len(questions):
                text = quiz_results(current_player.get_answers())
                answer_to_client(chat_id=chat_id, text=text, parse_mode='HTML')

            elif check_last_answers(current_player.get_question_id(), callback):
                answer_to_client(chat_id=chat_id, text='Ая-яй! Вы уже ответили на этот вопрос :)')
                player_q_id = current_player.get_question_id()
                reply_markup = make_keyboard(player_q_id)
                answer_to_client(chat_id=chat_id, text=questions[player_q_id]['question'], reply_markup=reply_markup)

            else:
                current_player.get_question_id(1)
                current_player.get_answers(callback)

                reply_markup = make_keyboard(current_player.get_question_id())
                answer_to_client(chat_id=chat_id, text=questions[current_player.get_question_id()]['question'], reply_markup=reply_markup)


        elif check_private_message(r):
            chat_id = r['message']['chat']['id']
            message = r['message']['text']

            if message.lower() == quiz_start:
                current_player = Player(chat_id)

                if current_player.player == None:
                    current_player.restart_player(question_id=0, answers=[])
                    reply_markup = make_keyboard(0)
                    answer_to_client(chat_id=chat_id, text=questions[0]['question'], reply_markup=reply_markup)

                elif current_player.get_question_id() == len(questions):
                    text = quiz_results(current_player.get_answers())
                    answer_to_client(chat_id=chat_id, text=text, parse_mode='HTML')

                else:
                    player_q_id = current_player.get_question_id()
                    reply_markup = make_keyboard(player_q_id)
                    answer_to_client(chat_id=chat_id, text=questions[player_q_id]['question'], reply_markup=reply_markup)

            elif message.lower() in quiz_restart:
                current_player = Player(chat_id)

                if current_player.player == None:
                    answer_to_client(chat_id=chat_id, text='Вы еще даже не проходили викторину. Как я начну еще раз?')
                    answer_to_client(chat_id=chat_id, text="Напишите мне лучше слово 'Викторина'!")

                elif len(current_player.get_answers()) != len(questions) and len(current_player.get_answers()) > 0:
                    answer_to_client(chat_id=chat_id, text="Вы еще не завершили викторину, чтобы начать сначала :)")
                    reply_markup = make_keyboard(current_player.get_question_id())
                    answer_to_client(chat_id=chat_id, text=questions[current_player.get_question_id()]['question'], reply_markup=reply_markup)
                
                else:
                    current_player.restart_player(question_id=0, answers=[])
                    reply_markup = make_keyboard(0)
                    answer_to_client(chat_id=chat_id, text=questions[0]['question'], reply_markup=reply_markup)

            else:
                answer_to_client(chat_id=chat_id, text=QUIZ_INFO)

        else:
            chat_id = r['message']['chat']['id']
            answer_to_client(chat_id=chat_id, text='Я работаю только с текстом, друг мой :)')

    return jsonify(r)



if __name__ == '__main__':
    app.run()

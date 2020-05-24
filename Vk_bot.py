from vk_api import *
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from jokes_and_stickers import Jokes
from jokes_and_stickers import FunStickers
from jokes_and_stickers import WhatStickers
from utils import Updater, WinCode, RW
from datetime import date, datetime
from random import randint
from requests import get
from re import findall
from threading import Thread


class Bot:
    # инициализация_бота------------------------------------------------------------------------------------------------
    def __init__(self, bot_name, api_token, group_id):
        # имя_бота_и_id_группы
        self.bot_name = bot_name.lower()
        self.__group_id = group_id
        # администрация_бота
        self.__admin_id = 459738162
        self.__leadership = [self.__admin_id]
        # инициализация_токена_и_api
        self.__vk = VkApi(token=api_token)
        self.__upload = VkUpload(self.__vk)
        self.__long_poll = VkBotLongPoll(self.__vk, group_id=self.__group_id)
        self.__vk_api = self.__vk.get_api()
        # переменная_для_событий_(сообщений)
        self.__event = None
        # ценовые_переменные
        self.__first_bonus = 150
        # self.__lottery_price = 100
        # инициализация_клаввиатур
        self.__main_keyboard = self.__init_main_keyboard()
        self.__sel_group_keyboard = self.__init_sel_group_keyboard()
        self.__sel_week_day_keyboard = self.__init_sel_week_day_keyboard()
        # self.__lottery_keyboard = self.__init_lottery_keyboard()
        # дополнительные_переменные
        self.__group_num = dict()
        self.__excel_date = date(2020, 1, 1)
        self.__zp_day = date(2020, 1, 1)
        # падежные_окончания_названия_валюты
        self.__dub = ('ов', '', 'а', 'а', 'а', 'ов', 'ов', 'ов', 'ов', 'ов')
        # фильтр_луп
        self.__filter = [<filter_list>]
        # генерация_кода_для_экстренного_созыва_беседы
        self.__emergency_code = self.__generating_emergency_code()
        # отрпавка_кода_для_экстренного_созыва_беседы
        self.__give_emergency_code(self.__emergency_code)
        # инициализация_потока_ожидания_событий
        self.thread = Thread(target=Updater,
                             args=(self.__vk_api,
                                   self.__dub,
                                   self.__load_pic('personal_accounts/win_pic/honks.jpg'),
                                   self.__load_pic('workout_pic/0.jpg'),
                                   self.__load_pic('personal_accounts/win_pic/not_stonks.png')),
                             daemon=True)
        self.thread_2 = Thread(target=self.__activate,
                               args=(),
                               daemon=True)
        # запуск_потока_ожидания_событий
        #self.thread_2.start()
        self.thread.start()
        # запуск_прослушивания_бота
        self.__listen_events()

    # прослушка_всех_сообщений------------------------------------------------------------------------------------------
    def __listen_events(self):
        while True:
            try:
                for event in self.__long_poll.listen():
                    self.__event = event
                    if not self.__event.object.message['text'] == '':
                        if event.from_chat:
                            self.__processing_chat_messages()
                        elif event.from_user:
                            self.__processing_personal_messages()
            except SystemExit:
                raise SystemExit
            except Exception as error:
                print(error)
                # WriteLog(self.__event.object.message['from_id'],
                #          'The main exception was eliminated!!!\n' + str(error),
                #          'None')

    # обработка_сообщений_чата------------------------------------------------------------------------------------------
    def __processing_chat_messages(self):
        message = self.__event.object.message['text'].lower()
        if self.bot_name in message or str(self.__group_id) in message:
            message = self.__deleting_the_bot_name(message, self.bot_name)
            # общий_сбор------------------------------------------------------------------------------------------------
            if self.__emergency_code in message:
                self.__call_everyone()
                self.__emergency_code = self.__generating_emergency_code()
                self.__give_emergency_code(self.__emergency_code)
            # запрос_расписания-----------------------------------------------------------------------------------------
            elif 'расписани' in message or 'пар' in message or 'кабинет' in message or 'урок' in message or\
                    'предмет' in message:
                self.__get_group()
            elif 'группа №1' in message or 'группа №2' in message or 'группа №3' in message:
                self.__get_day_of_week(message)
            elif 'понедельник' in message or 'вторник' in message or 'среда' in message or 'четверг' in message or\
                    'пятница' in message or 'на всю неделю' in message:
                self.__give_response_schedule(message)
            # запрос_баланса--------------------------------------------------------------------------------------------
            elif 'баланс' in message:
                self.__give_response_my_balance()
            # запрос_курса_перевод--------------------------------------------------------------------------------------
            elif 'переве' in message or 'перевод' in message:
                self.__give_response_money_transfer(message)
            # запрос_курса_Дубасов--------------------------------------------------------------------------------------
            elif 'курс' in message:
                self.__give_response_course()
            # запрос_погоды---------------------------------------------------------------------------------------------
            elif 'погод' in message:
                self.__give_response_weather()
            # запрос_на_шутку-------------------------------------------------------------------------------------------
            elif 'анекдот' in message or 'шут' in message or 'рофл' in message:
                # не_говорить-------------------------------------------------------------------------------------------
                if 'не ' in message or 'ненави' in message:
                    self.__give_response_no_joke()
                # говорить----------------------------------------------------------------------------------------------
                else:
                    self.__give_response_joke()
                    self.__give_response_joke_sticker()
            # # отправка_клаввиатуры_для_лотереи--------------------------------------------------------------------------
            # elif 'лотерея' in message or 'казино' in message:
            #     self.__give_lottery_keyboard()
            # # отправка_ответа_на_выбор_лота_для_ставки------------------------------------------------------------------
            # elif 'зелёное' in message or 'красное' in message:
            #     self.__give_response_lottery(message)
            # отправка_ответа_монетки-----------------------------------------------------------------------------------
            elif 'монет' in message:
                self.__give_response_coin()
            # вопрос_'а_где_же_лупа?'-----------------------------------------------------------------------------------
            elif 'луп' in message and self.__zp_day != date.today():
                self.__give_response_lupa()
                self.__zp_day = date.today()
            # запрос_всех_команд----------------------------------------------------------------------------------------
            elif 'команд' in message or 'мог' in message:
                self.__give_response_all_command()
            # запрос_создателей-----------------------------------------------------------------------------------------
            elif 'созда' in message or 'сдел' in message or 'произв' in message or 'разраб' in message:
                self.__give_response_about_creator()
            # ошибочный_запрос------------------------------------------------------------------------------------------
            else:
                self.__give_response_error()

    # обработка_персональных_сообщений----------------------------------------------------------------------------------
    def __processing_personal_messages(self):
        message = self.__deleting_the_bot_name(self.__event.object.message['text'].lower(), self.bot_name)
        # запрос_расписания-----------------------------------------------------------------------------------------
        if 'расписани' in message or 'пар' in message or 'кабинет' in message or 'урок' in message or\
                'предмет' in message:
            self.__get_group()
        elif 'группа №1' in message or 'группа №2' in message or 'группа №3' in message:
            self.__get_day_of_week(message)
        elif 'понедельник' in message or 'вторник' in message or 'среда' in message or 'четверг' in message or\
                'пятница' in message or 'на всю неделю' in message:
            self.__give_response_schedule(message)
        # запрос_баланса------------------------------------------------------------------------------------------------
        elif 'баланс' in message:
            self.__give_response_my_balance()
        # запрос_курса_перевод------------------------------------------------------------------------------------------
        elif 'переве' in message or 'перевод' in message:
            self.__give_response_money_transfer(message)
        # запрос_курса_Дубасов------------------------------------------------------------------------------------------
        elif 'курс' in message:
            self.__give_response_course()
        # запрос_погоды-------------------------------------------------------------------------------------------------
        elif 'погод' in message:
            self.__give_response_weather()
        # запрос_на_шутку-----------------------------------------------------------------------------------------------
        elif 'анекдот' in message or 'шут' in message or 'рофл' in message:
            # не_говорить-----------------------------------------------------------------------------------------------
            if 'не ' in message or 'ненави' in message:
                self.__give_response_no_joke()
            # говорить--------------------------------------------------------------------------------------------------
            else:
                self.__give_response_joke()
                self.__give_response_joke_sticker()
        # # отправка_клаввиатуры_для_лотереи------------------------------------------------------------------------------
        # elif 'лотерея' in message or 'казино' in message:
        #     self.__give_lottery_keyboard()
        # # отправка_ответа_на_выбор_лота_для_ставки----------------------------------------------------------------------
        # elif 'зелёное' in message or 'красное' in message:
        #     self.__give_response_lottery(message)
        # отправка_ответа_монетки---------------------------------------------------------------------------------------
        elif 'монет' in message:
            self.__give_response_coin()
        # запрос_всех_команд--------------------------------------------------------------------------------------------
        elif 'команд' in message or 'мог' in message:
            self.__give_response_all_command()
        # запрос_создателей---------------------------------------------------------------------------------------------
        elif 'созда' in message or 'сдел' in message or 'произв' in message or 'разраб' in message:
            self.__give_response_about_creator()
        # запрос_файла_и_выхода-----------------------------------------------------------------------------------------
        elif 'raise exit' in message and self.__event.object.message['from_id'] == self.__admin_id:
            self.__give_file()
        # ошибочный_запрос----------------------------------------------------------------------------------------------
        else:
            self.__give_response_error()

    # отправка_монетки--------------------------------------------------------------------------------------------------
    def __give_response_coin(self):
        random_id = get_random_id()
        __items = ['Орёл', 'Решка']
        __word_end = ['', 'а']
        coin = randint(0, 1)
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=f'Выпал{__word_end[coin]}: {__items[coin]}'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # отправка_файла_и_инициализация_выхода-----------------------------------------------------------------------------
    def __give_file(self):
        random_id = get_random_id()
        users = RW.read_file('personal_accounts/accounts.dat')
        users = '\n'.join([f'{i} {users[i]}' for i in users])
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__admin_id,
                                    message=users
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

        with open("block.pid", "w") as file:
            # create empty file
            pass

        raise SystemExit

    # отправка_клаввиатуры_для_лотереи----------------------------------------------------------------------------------
    def __give_lottery_keyboard(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__lottery_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=f'Выберите номер на который хотите поставить'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # регестрация_в_лотерее---------------------------------------------------------------------------------------------
    def __give_response_lottery(self, message):
        random_id = get_random_id()
        __temp_bank_users = RW.read_file('personal_accounts/accounts.dat')
        __temp_lottery_users = RW.read_file('lottery_participant/participant.dat')
        user = self.__event.object.message['from_id']
        user_name = '@' + self.__vk_api.users.get(user_ids=user, fields='screen_name')[0]['screen_name']
        ints = findall(r'\d+', message)
        if len(ints):
            if 11 > int(ints[0]) > 0:
                if user in __temp_bank_users:
                    if user not in __temp_lottery_users:
                        if __temp_bank_users[user] >= self.__lottery_price:
                            __temp_bank_users[user] -= self.__lottery_price
                            rate = WinCode.code_str_to_int(message)
                            RW.write_file('lottery_participant/participant.dat', 'a', {f'{user}': rate})
                            RW.write_file('personal_accounts/accounts.dat', 'w', __temp_bank_users)
                            self.__vk_api.messages.send(random_id=random_id,
                                                        keyboard=self.__main_keyboard,
                                                        peer_id=self.__event.object.message['peer_id'],
                                                        message=f'{user_name} ваша ставка принята!!!\n' +
                                                                f'Ожидайте розыгрыша\n' +
                                                                f'Розыгрыш проводится каждый день с 10:00 до 11:00' +
                                                                f' и с 16:00 до 17:00'
                                                        )
                            # WriteLog(self.__event.object.message['from_id'],
                            #          self.__event.object.message['text'],
                            #          random_id)
                        else:
                            self.__vk_api.messages.send(random_id=random_id,
                                                        keyboard=self.__main_keyboard,
                                                        peer_id=self.__event.object.message['peer_id'],
                                                        message=f'У вас не хватает денег на лотерею...\n' +
                                                                f'Добро пожаловать в Низший класс населения России\n' +
                                                                f'Вы можете занять деняг у друзей, взять в кредит или'
                                                                f' продолжить жить в "СТАБИЛЬНОСТИ"'
                                                        )
                            # WriteLog(self.__event.object.message['from_id'],
                            #          self.__event.object.message['text'],
                            #          random_id)
                    else:
                        self.__vk_api.messages.send(random_id=random_id,
                                                    keyboard=self.__main_keyboard,
                                                    peer_id=self.__event.object.message['peer_id'],
                                                    message=f'Вы уже поставили на "' +
                                                            f'{WinCode.code_int_to_str(__temp_lottery_users[user])}' +
                                                            f'"!!!\n' +
                                                            f'Ожидайте розыгрыша\n' +
                                                            f'Розыгрыш проводится каждый день с 10:00 до 11:00' +
                                                            f' и с 16:00 до 17:00'
                                                    )
                        # WriteLog(self.__event.object.message['from_id'],
                        #          self.__event.object.message['text'],
                        #          random_id)
                else:
                    self.__vk_api.messages.send(random_id=random_id,
                                                keyboard=self.__main_keyboard,
                                                peer_id=self.__event.object.message['peer_id'],
                                                message=f'У вас нет единого электронного кошелька Дубасов,' +
                                                        f' по этому вы не можете учавствовать в лотерее!!!'
                                                )
                    # WriteLog(self.__event.object.message['from_id'],
                    #          self.__event.object.message['text'],
                    #          random_id)
            else:
                self.__vk_api.messages.send(random_id=random_id,
                                            keyboard=self.__main_keyboard,
                                            peer_id=self.__event.object.message['peer_id'],
                                            message=f'Допустимо ставить лишь на номера от 1 (включительно) до 10' +
                                                    f' (включительно)!!!'
                                            )
                # WriteLog(self.__event.object.message['from_id'],
                #          self.__event.object.message['text'],
                #          random_id)
        else:
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=self.__event.object.message['peer_id'],
                                        message=f'Вы не указали номер на который хотите поставить!!!'
                                        )
            # WriteLog(self.__event.object.message['from_id'],
            #          self.__event.object.message['text'],
            #          random_id)

    # отправка_погоды---------------------------------------------------------------------------------------------------
    def __give_response_weather(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=self.__get_weather()
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # получение_погоды--------------------------------------------------------------------------------------------------
    @staticmethod
    def __get_weather():
        s_city = 'Moscow,ru'
        token = "<Weather_token>"
        k = 273.15
        weather = get(f"https://api.openweathermap.org/data/2.5/weather?q={s_city}&APPID={token}").json()
        out = f"В Москве сейчас:\n" + \
              f"Температура: {round(weather['main']['temp'] - k, 2)} °C\n" + \
              f"По ощущениям: {round(weather['main']['feels_like'] - k, 2)} °C\n" + \
              f"Ветер: {weather['wind']['speed']} м/с\n" + \
              f"Статус погоды: {weather['weather'][0]['description']}\n" + \
              f"Давление: {weather['main']['pressure']} гПа\n" + \
              f"Влажность: {weather['main']['humidity']} %\n" + \
              f"Восход солнца: {datetime.fromtimestamp(weather['sys']['sunrise']).strftime('%H:%M')}\n" + \
              f"Заход солнца: {datetime.fromtimestamp(weather['sys']['sunset']).strftime('%H:%M')}"
        return out

    # удаление_лобого_упоминания_бота-----------------------------------------------------------------------------------
    @staticmethod
    def __deleting_the_bot_name(text, bot_name):
        text = text.replace(bot_name, '')
        while 'club' in text:
            target_str = text[text.find('club') - 1:]
            target_str = target_str[:target_str.find(']') + 1]
            text = text.replace(target_str, '')
        return text

    # ответ_на_запрос_перевода------------------------------------------------------------------------------------------
    def __give_response_money_transfer(self, message):
        random_id = get_random_id()
        __temp_client_dict = RW.read_file('personal_accounts/accounts.dat')
        __user_id = self.__event.object.message['from_id']
        __user_name = '@' + self.__vk_api.users.get(user_ids=__user_id,
                                                    fields='screen_name')[0]['screen_name']
        __payee_id, message = self.__get_target_address(message)
        if len(findall(r'\d+', message)):
            if __payee_id is None:
                self.__vk_api.messages.send(random_id=random_id,
                                            keyboard=self.__main_keyboard,
                                            peer_id=self.__event.object.message['peer_id'],
                                            message=f'Вы не указали получателя!!!'
                                            )
                # WriteLog(self.__event.object.message['from_id'],
                #          self.__event.object.message['text'],
                #          random_id)
            elif __user_id in __temp_client_dict:
                __payee_name = '@' + self.__vk_api.users.get(user_ids=__payee_id,
                                                             fields='screen_name')[0]['screen_name']
                if __payee_id in __temp_client_dict:
                    __transfer_amount = int(findall(r'\d+', message)[0])
                    if __temp_client_dict[__user_id] >= __transfer_amount:
                        __temp_client_dict[__user_id] -= __transfer_amount
                        __temp_client_dict[__payee_id] += __transfer_amount
                        RW.write_file('personal_accounts/accounts.dat', 'w', __temp_client_dict)
                        self.__vk_api.messages.send(random_id=random_id,
                                                    keyboard=self.__main_keyboard,
                                                    peer_id=self.__event.object.message['peer_id'],
                                                    message=f'Перевод на сумму {__transfer_amount}' +
                                                            f' Дубас{self.__dub[__transfer_amount % 10]} успешно' +
                                                            f' совершён!!!\n' +
                                                            f'Отправитель: {__user_name}\n' +
                                                            f'Получатель: {__payee_name}'
                                                    )
                        # WriteLog(self.__event.object.message['from_id'],
                        #          self.__event.object.message['text'],
                        #          random_id)
                    else:
                        self.__vk_api.messages.send(random_id=random_id,
                                                    keyboard=self.__main_keyboard,
                                                    peer_id=self.__event.object.message['peer_id'],
                                                    message=f'У вас недостатоно средств для совершения перевода на ' +
                                                            f'данную сумму!!!'
                                                    )
                        # WriteLog(self.__event.object.message['from_id'],
                        #          self.__event.object.message['text'],
                        #          random_id)
                else:
                    self.__vk_api.messages.send(random_id=random_id,
                                                keyboard=self.__main_keyboard,
                                                peer_id=self.__event.object.message['peer_id'],
                                                message=f'У {__payee_name} пока нет электронного Дубасного' +
                                                        f' кошелька!!!\n' +
                                                        f'Чтобы его завести - запросите баланс, кошелёк будет' +
                                                        f' автоматически привязан к вашему аккаунту!'
                                                )
                    # WriteLog(self.__event.object.message['from_id'],
                    #          self.__event.object.message['text'],
                    #          random_id)
            else:
                self.__vk_api.messages.send(random_id=random_id,
                                            keyboard=self.__main_keyboard,
                                            peer_id=self.__event.object.message['peer_id'],
                                            message=f'У вас пока нет электронного Дубасного кошелька!!!\n' +
                                            f'Чтобы его завести - запросите баланс, кошелёк будет автоматически' +
                                            f' привязан к вашему аккаунту!'
                                            )
                # WriteLog(self.__event.object.message['from_id'],
                #          self.__event.object.message['text'],
                #          random_id)
        else:
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=self.__event.object.message['peer_id'],
                                        message=f'Вы не указали сумму перевода!!!'
                                        )
            # WriteLog(self.__event.object.message['from_id'],
            #          self.__event.object.message['text'],
            #          random_id)

    # ответ_на_запрос_баланса-------------------------------------------------------------------------------------------
    def __give_response_my_balance(self):
        random_id = get_random_id()
        __temp_client_dict = RW.read_file('personal_accounts/accounts.dat')
        __user_id = self.__event.object.message['from_id']
        __user_name = '@' + self.__vk_api.users.get(user_ids=__user_id,
                                                    fields='screen_name')[0]['screen_name']
        if __user_id in __temp_client_dict:
            balance = __temp_client_dict[__user_id]
            del __temp_client_dict
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=self.__event.object.message['peer_id'],
                                        message=f'{__user_name}, ваш баланс: {balance} Дубас{self.__dub[balance % 10]}'
                                        )
            # WriteLog(self.__event.object.message['from_id'],
            #          self.__event.object.message['text'],
            #          random_id)
        else:
            RW.write_file('personal_accounts/accounts.dat', 'a', {f'{__user_id}': self.__first_bonus})
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=self.__event.object.message['peer_id'],
                                        message=f'{__user_name} поздравляем с регистрацией Дубасного лицевого ' +
                                                f'счета!!!\n' +
                                                f'Вам начислен бонус в размере: ' +
                                                f'{self.__first_bonus} Дубас{self.__dub[self.__first_bonus % 10]}\n' +
                                                f'Ваш баланс: {self.__first_bonus} ' +
                                                f'Дубас{self.__dub[self.__first_bonus % 10]}'
                                        )
            # WriteLog(self.__event.object.message['from_id'],
            #          self.__event.object.message['text'],
            #          random_id)

    # вычленение_id_из_сообщения----------------------------------------------------------------------------------------
    @staticmethod
    def __get_target_address(text):
        out = text[text.find('id') + 2:text.find('|')]
        if out.isdigit():
            return int(out), text.replace(text[text.find('['):text.find(']') + 1], '')
        else:
            return None, text

    # всеобщий_сбор-----------------------------------------------------------------------------------------------------
    def __call_everyone(self):
        random_id = get_random_id()
        user_profile = self.__vk_api.messages.getConversationMembers(
            peer_id=self.__event.object.message['peer_id'])['profiles']
        user_profile = ' '.join([f"@{i['screen_name']}" for i in user_profile])
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=user_profile
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    @staticmethod
    def __activate():
        bot = Lupa()
        bot.run(TOKEN)

    # рассылка_кода_вызова----------------------------------------------------------------------------------------------
    def __give_emergency_code(self, code):
        for i in self.__leadership:
            random_id = get_random_id()
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=i,
                                        message=f'Ваш код для экстренного созыва:')
            random_id = get_random_id()
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=i,
                                        message=code)
            # WriteLog('None',
            #          f"request: <emergency_code>",
            #          random_id)

    # генерация_кода_вызова---------------------------------------------------------------------------------------------
    @staticmethod
    def __generating_emergency_code():
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
        return ''.join([alphabet[randint(0, len(alphabet) - 1)] for i in range(20)])

    # инициализация_меню_клаввиатуры------------------------------------------------------------------------------------
    def __init_main_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Погода', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Баланс Дубасов', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Монетка', color=VkKeyboardColor.PRIMARY)
        # keyboard.add_line()
        # keyboard.add_button(f'Лотерея (Цена: {self.__lottery_price} Дубасов)', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    # инициализация_меню_клаввиатуры------------------------------------------------------------------------------------
    @staticmethod
    def __init_sel_group_keyboard():
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Группа №1', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Группа №2', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Группа №3', color=VkKeyboardColor.POSITIVE)
        return keyboard.get_keyboard()

    # инициализация_меню_клаввиатуры------------------------------------------------------------------------------------
    @staticmethod
    def __init_sel_week_day_keyboard():
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Понедельник', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Вторник', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Среда', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Четверг', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Пятница', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('На всю неделю', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    # инициализация_лотерейной_клаввиатуры------------------------------------------------------------------------------
    @staticmethod
    def __init_lottery_keyboard():
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('1 красное', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('1 зелёное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('2 зелёное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('2 красное', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('3 красное', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('3 зелёное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('4 зелёное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('4 красное', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    # ответ_на_запрос_курса---------------------------------------------------------------------------------------------
    def __give_response_course(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message='Нынешний курс:\n\n' +
                                    'Покупка Дубасов:\n' +
                                    '1 Дубас <- 42 Рублей\n' +
                                    '1 Дубас <- 1050000 Долларов\n' +
                                    '1 Дубас <- 1,05 Евро\n\n' +
                                    'Продажа дубасов:\n' +
                                    '1 Дубас -> 40 Рублей\n' +
                                    '1 Дубас -> 1000000 Долларов\n' +
                                    '1 Дубас -> 1 Евро')
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # ответ_на_вопрос_про_создателей------------------------------------------------------------------------------------
    def __give_response_about_creator(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=f'Над моим созданием трудилась небольшая группа людей:\n' +
                                    '@duuuda - программист, разработчик\n' +
                                    '@valeratv2013 - дизайнер сообщества, тестировщик\n' +
                                    '@ptsesh - спонсор (владелец хоста), тестировщик\n' +
                                    '@id274089649 - pre-α тестировщик\n' +
                                    '@cephalon_ordis - спонсор (владелец хоста)'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # ответ_на_вопрос_про_лупу------------------------------------------------------------------------------------------
    def __give_response_lupa(self):
        random_id = get_random_id()
        user_profile = self.__vk_api.messages.getConversationMembers(
            peer_id=self.__event.object.message['peer_id'])['profiles']
        user_profile = [f"{i['first_name']} {i['last_name']}" for i in user_profile]
        user_profile = list(filter(lambda x: x not in self.__filter, user_profile))
        user_profile = user_profile[randint(0, len(user_profile) - 1)]
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=f'Сегодня Лупы с нами нет. Так, что {user_profile} сегодня получит за Лупу'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # отправка_клаввиатуры_для_выбора_группы----------------------------------------------------------------------------
    def __get_group(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__sel_group_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message='Выберите группу'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # отправка_клаввиатуры_для_выбора_дня_недели------------------------------------------------------------------------
    def __get_day_of_week(self, message):
        random_id = get_random_id()
        if '1' in message:
            self.__group_num[self.__event.object.message['peer_id']] = 1
        elif '2' in message:
            self.__group_num[self.__event.object.message['peer_id']] = 2
        elif '3' in message:
            self.__group_num[self.__event.object.message['peer_id']] = 3
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__sel_week_day_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message='Выберите день недели'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # выдача_расписания-------------------------------------------------------------------------------------------------
    def __give_response_schedule(self, message):
        random_id = get_random_id()
        if self.__event.object.message['peer_id'] in self.__group_num:
            if 'понедельник' in message:
                self.__give_response_schedule_for_a_day(self.__group_num[self.__event.object.message['peer_id']], 1)
                del self.__group_num[self.__event.object.message['peer_id']]
            elif 'вторник' in message:
                self.__give_response_schedule_for_a_day(self.__group_num[self.__event.object.message['peer_id']], 2)
                del self.__group_num[self.__event.object.message['peer_id']]
            elif 'среда' in message:
                self.__give_response_schedule_for_a_day(self.__group_num[self.__event.object.message['peer_id']], 3)
                del self.__group_num[self.__event.object.message['peer_id']]
            elif 'четверг' in message:
                self.__give_response_schedule_for_a_day(self.__group_num[self.__event.object.message['peer_id']], 4)
                del self.__group_num[self.__event.object.message['peer_id']]
            elif 'пятница' in message:
                self.__give_response_schedule_for_a_day(self.__group_num[self.__event.object.message['peer_id']], 5)
                del self.__group_num[self.__event.object.message['peer_id']]
            elif 'на всю неделю' in message:
                self.__give_response_schedule_for_a_week(self.__group_num[self.__event.object.message['peer_id']])
                del self.__group_num[self.__event.object.message['peer_id']]
        else:
            self.__vk_api.messages.send(random_id=random_id,
                                        keyboard=self.__main_keyboard,
                                        peer_id=self.__event.object.message['peer_id'],
                                        message='Вы забыли указать номер группы!!!'
                                        )
            # WriteLog(self.__event.object.message['from_id'],
            #          self.__event.object.message['text'],
            #          random_id)

    # выдача_расписания_на_неделю---------------------------------------------------------------------------------------
    def __give_response_schedule_for_a_week(self, group_num):
        random_id = get_random_id()
        attachment = str()
        for day_of_week in range(1, 6):
            attachment += self.__load_pic(f'excel_parser/schedule/{group_num}/{day_of_week}.png') + ','
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message='Вот ваше расписание!',
                                    attachment=attachment[:-1]
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # выдача_расписания_на_день-----------------------------------------------------------------------------------------
    def __give_response_schedule_for_a_day(self, group_num, day_num):
        random_id = get_random_id()
        attachment = self.__load_pic(f'excel_parser/schedule/{group_num}/{day_num}.png')
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message='Вот ваше расписание!',
                                    attachment=attachment
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # загрузка_изображения----------------------------------------------------------------------------------------------
    def __load_pic(self, photo_path):
        photo = self.__upload.photo_messages(photo_path)
        owner_id = photo[0]['owner_id']
        photo_id = photo[0]['id']
        access_key = photo[0]['access_key']
        return f'photo{owner_id}_{photo_id}_{access_key}'

    # отправка_"НЕ_шутки"-----------------------------------------------------------------------------------------------
    def __give_response_no_joke(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    sticker_id=15899
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # отправка_шутки----------------------------------------------------------------------------------------------------
    def __give_response_joke(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message=Jokes().random_joke()
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # отправка_смайлика_шутки-------------------------------------------------------------------------------------------
    def __give_response_joke_sticker(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    sticker_id=FunStickers().random_sticker()
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          f'sticker sent',
        #          random_id)

    # отправка_всех_комманд---------------------------------------------------------------------------------------------
    def __give_response_all_command(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    message='Вы можете:\n' +
                                            '— Попросить меня дать расписание\n' +
                                            '— Попросить рассказать шутку/анекдот/рофл\n' +
                                            '— Спросить список всех команд\n' +
                                            '— Спросить кто меня создал\n' +
                                            '— Узнать курс Дубасов\n' +
                                            '— Перевести Дубасы\n' +
                                            '— Подбросить монетку\n' +
                                            '— и многое другое!\n' +
                                            'В беседах обращайтесь ко мне по имени!'
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

    # отправка_недопонимания--------------------------------------------------------------------------------------------
    def __give_response_error(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    keyboard=self.__main_keyboard,
                                    peer_id=self.__event.object.message['peer_id'],
                                    sticker_id=WhatStickers().random_sticker()
                                    )
        # WriteLog(self.__event.object.message['from_id'],
        #          self.__event.object.message['text'],
        #          random_id)

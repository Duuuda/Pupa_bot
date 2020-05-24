from excel_parser import ExcelParser
from os.path import abspath
from datetime import datetime
from random import randint
from time import sleep
from vk_api.utils import get_random_id
from datetime import time
from re import findall


class Updater:
    # инициализация_отчлеживания_событий--------------------------------------------------------------------------------
    def __init__(self, vk_api, dub, win_pic, workout_pic, not_win_pic):
        self.__win_obj = WinCode(vk_api)
        self.__update_schedule = Event(time(4, 0), UpdateSchedule)
        # self.__give_prize = Event([10, 16], GivePrize, (vk_api, dub, self.__win_obj, win_pic, not_win_pic))
        self.__workout_remind = Event(time(11, 0), WorkoutRemind, (vk_api, workout_pic))
        self.__update_schedule.start_event()
        print('Bot is running!\n')
        self.__start_update_check()

    # цикл_ожидания_событий---------------------------------------------------------------------------------------------
    def __start_update_check(self):
        while True:
            if datetime.now().hour == self.__update_schedule.time.hour:
                self.__update_schedule.start_event()
            # elif datetime.now().hour in self.__give_prize.time:
            #     self.__give_prize.start_event()
            elif datetime.now().hour == self.__workout_remind.time.hour:
                self.__workout_remind.start_event()
            sleep(3600)


# напоминание_о_тренировке----------------------------------------------------------------------------------------------
class WorkoutRemind:
    def __init__(self, vk_api, workout_pic):
        self.__vk_api = vk_api
        self.__workout_pic = workout_pic
        self.__remind()

    def __remind(self):
        random_id = get_random_id()
        self.__vk_api.messages.send(random_id=random_id,
                                    peer_id=305775300,
                                    message=f'Пи*дуй заниматься!!!\n' +
                                            f'Иначе станешь такой!!!',
                                    attachment=self.__workout_pic
                                    )
        #WriteLog('None', '<workout reminder>', random_id)


# выдача_призов---------------------------------------------------------------------------------------------------------
class GivePrize:
    def __init__(self, vk_api, dub, win_obj, win_pic, not_win_pic):
        self.__vk_api = vk_api
        self.__dub = dub
        self.__win_obj = win_obj
        self.__win_pic = win_pic
        self.__not_win_pic = not_win_pic
        self.__conv_peer_id = 2000000004  # 2000000002
        self.__give()

    def __give(self):
        random_id = get_random_id()
        __all_lottery_users = RW.read_file('lottery_participant/participant.dat')
        __all_users = len(__all_lottery_users)
        RW.write_file('lottery_participant/participant.dat', 'w', {})
        if len(__all_lottery_users):  # --------------------------------------------------------------------------------
            __all_lottery_users = {i: {'nik': '@' + self.__vk_api.users.get(user_ids=i,
                                                                            fields='screen_name')[0]['screen_name'],
                                       'win': 0}
                                   for i in __all_lottery_users
                                   if __all_lottery_users[i] == self.__win_obj.code}
            if len(__all_lottery_users):  # ----------------------------------------------------------------------------
                __all_winners = len(__all_lottery_users)
                for i in __all_lottery_users:
                    __all_lottery_users[i]['win'] = (__all_users * 100 // __all_winners) + 100
                __all_bank_users = RW.read_file('personal_accounts/accounts.dat')
                for i in __all_lottery_users:
                    __all_bank_users[i] += __all_lottery_users[i]['win']
                RW.write_file('personal_accounts/accounts.dat', 'w', __all_bank_users)
                del __all_bank_users
                __prepared_data = '\n'.join([f'{__all_lottery_users[i]["nik"]} +{__all_lottery_users[i]["win"]} Дубас' +
                                             f'{self.__dub[__all_lottery_users[i]["win"] % 10]}'
                                             for i in __all_lottery_users])
                self.__vk_api.messages.send(random_id=random_id,
                                            peer_id=self.__conv_peer_id,
                                            message=f'Сегодня в нашей лотерее победил' +
                                                    f'{"" if len(__all_lottery_users) == 1 else "и"}:\n' +
                                                    __prepared_data +
                                                    f'\nПоздравляем победител'
                                                    f'{"я" if len(__all_lottery_users) == 1 else "ей"}!!!',
                                            attachment=self.__win_pic
                                            )
                #WriteLog('None', f'raffle', random_id)
            else:  # ---------------------------------------------------------------------------------------------------
                self.__vk_api.messages.send(random_id=random_id,
                                            peer_id=self.__conv_peer_id,
                                            message=f'Сегодня в нашей лотерее, к сожалению, никто не победил :(',
                                            attachment=self.__not_win_pic
                                            )
                #WriteLog('None', f'raffle', random_id)
        else:  # -------------------------------------------------------------------------------------------------------
            self.__vk_api.messages.send(random_id=random_id,
                                        peer_id=self.__conv_peer_id,
                                        message=f'Сегодня в нашем ежедневном розыгрыше никто не победил...\n' +
                                                f'Потому что никто не сделал ставок!!!\n' +
                                                f'Простите, девачки, я снова плачу'
                                        )
            #WriteLog('None', f'raffle', random_id)
            random_id = get_random_id()
            self.__vk_api.messages.send(random_id=random_id,
                                        peer_id=self.__conv_peer_id,
                                        sticker_id=15899
                                        )
            #WriteLog('None', f'raffle_sticker', random_id)
        self.__win_obj.re_gen_code()


# класс_чтения/записи_файлов--------------------------------------------------------------------------------------------
class RW:
    # чтение_файла------------------------------------------------------------------------------------------------------
    @staticmethod
    def read_file(file_path):
        file = open(file_path, 'r', encoding='UTF-8')
        __temp_client_dict = {int(client[:client.find(' ')]): int(client[client.find(' ') + 1:])
                              for client in file.read().split('\n') if client != ''}
        file.close()
        return __temp_client_dict

    # запись_в_файл-----------------------------------------------------------------------------------------------------
    @staticmethod
    def write_file(file_path, open_key, client_dict):
        __prepared_data = '\n'.join([f'{i} {client_dict[i]}' for i in client_dict])
        file = open(file_path, open_key, encoding='UTF-8')
        if open_key == 'w':
            file.write(__prepared_data)
        else:
            file.write('\n' + __prepared_data)
        file.close()


# обновление_расписания-------------------------------------------------------------------------------------------------
class UpdateSchedule:
    def __init__(self):
        try:
            ExcelParser().update_all_image(abspath('excel_parser/excel_file/book.xls'),
                                           abspath('excel_parser/schedule/back.png'),
                                           abspath('excel_parser/schedule/'),
                                           abspath('excel_parser/font/font.ttf'))
        except Exception as error:
            print(error)
            #WriteLog('None', 'The Thread exception was eliminated!!!\n' + str(error), 'None')


# вывод_лога_в_консоль_и_запись_в_файл----------------------------------------------------------------------------------
class WriteLog:
    def __init__(self, from_id, request, response_id):
        self.from_id = from_id
        self.request = request
        self.response_id = response_id
        self.__write()

    def __write(self):
        text = f"from id: {self.from_id}\n" +\
               f"time: {datetime.today()}\n" +\
               f"request: {self.request}\n" +\
               f"response id: {self.response_id}\n\n"
        file = open(f'logs/lg-{datetime.today().date()}.log', 'a', encoding='UTF-8')
        file.write(text)
        file.close()


# объект_выигрышного_числа----------------------------------------------------------------------------------------------
class WinCode:
    def __init__(self, vk_api):
        self.vk_api = vk_api
        self.code = int()
        self.str_code = str()
        self.__first_gen_code()

    @staticmethod
    def __gen_code():
        return randint(1, 4) * 10 + randint(1, 2)

    def __first_gen_code(self):
        file = open('lottery_participant/data.rwf', 'r', encoding='UTF-8')
        data = file.read()
        file.close()
        if data != '':
            self.code = int(data)
            self.str_code = self.code_int_to_str(self.code)
        else:
            self.re_gen_code()
        #self.__send_code()

    def re_gen_code(self):
        self.code = self.__gen_code()
        self.str_code = self.code_int_to_str(self.code)
        file = open('lottery_participant/data.rwf', 'w', encoding='UTF-8')
        file.write(str(self.code))
        file.close()
        #self.__send_code()

    @staticmethod
    def code_int_to_str(int_code):
        int_code = int(int_code)
        items = {1: 'красное', 2: 'зелёное'}
        return f'{int_code // 10} {items[int_code % 10]}'

    @staticmethod
    def code_str_to_int(str_code):
        str_code = str(str_code)
        ints = findall(r'\d+', str_code)
        if not len(ints):
            return 11
        elif 'красное' in str_code:
            return int(ints[0]) * 10 + 1
        else:
            return int(ints[0]) * 10 + 2

    def __send_code(self):
        random_id = get_random_id()
        self.vk_api.messages.send(random_id=random_id,
                                  peer_id=459738162,
                                  message=f'Код для ставки: {self.str_code}'
                                  )
        # WriteLog(459738162,
        #          '<win_code>',
        #          random_id)


# класс_события---------------------------------------------------------------------------------------------------------
class Event:
    def __init__(self, event_time=None, event=None, args=()):
        self.time = event_time
        self.event = event
        self.args = args
        self.event_complete = False

    def start_event(self):
        self.event(*self.args)

import xlrd
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from urllib.request import urlopen, urlretrieve
from os import system


class ExcelParser:
    # start_parse-------------------------------------------------------------------------------------------------------
    def update_all_image(self, book, back, schedule, font):
        # print('Tracert begins\n')  # ---------------------------------------------------------------------------------
        # system('tracert -h 60 muiv.ru')
        # print('Tracert ended')  # ------------------------------------------------------------------------------------

        print('Link receiving begins')  # ------------------------------------------------------------------------------
        with urlopen("https://www.muiv.ru/studentu/fakultety-i-kafedry/fakultet-it/raspisaniya/") as url:
            html = url.read().decode('UTF-8')
        end = html.find('">Выписка')
        start = html[:end].rfind('"') + 1
        link = 'https://www.muiv.ru' + html[start:end]
        print('Link receiving ended')  # -------------------------------------------------------------------------------

        print('Download begins')  # ------------------------------------------------------------------------------------
        urlretrieve(link, book)
        print('Download ended')  # -------------------------------------------------------------------------------------

        print('Pictures update have been started')  # ------------------------------------------------------------------
        self.__do_all_image(book, back, schedule, font)
        print('Pictures was updated')  # -----------------------------------------------------------------------------
        
    # do_all_image------------------------------------------------------------------------------------------------------
    def __do_all_image(self, book, back, schedule, font):
        for group in range(1, 4):
            for week_day in range(1, 6):
                self.__do_image(group, week_day, book, back, schedule, font)

    # do_one_image------------------------------------------------------------------------------------------------------
    def __do_image(self, group_num, num_of_day_of_week, book, back, schedule, font):
        data = self.__parse(group_num, num_of_day_of_week, book)
        text_time = '\n'.join(data[0])
        text_schedule = '\n'.join(data[1])
        font = ImageFont.truetype(font, 25)
        text_position = (5, 0)
        text_color = (0, 0, 0)
        img = Image.open(back)
        draw = ImageDraw.Draw(img)
        draw.text(text_position, text_time, text_color, font)
        text_position = (205, 0)
        draw.text(text_position, text_schedule, text_color, font)
        img.save(f'{schedule}/{group_num}/{num_of_day_of_week}.png')

    # parse_xls_file----------------------------------------------------------------------------------------------------
    def __parse(self, group_num, num_of_day_of_week, book):
        book = xlrd.open_workbook(book, formatting_info=True)
        sheet = book.sheet_by_index(0)
        week = {1: 'понедельник',
                2: 'вторник',
                3: 'среда',
                4: 'четверг',
                5: 'пятница',
                6: 'суббота',
                7: 'воскресенье'}

        day_coordinates = self.__find_ceil_coordinates(sheet, week[num_of_day_of_week])
        day_height = self.__get_height_of_day_of_week(sheet, day_coordinates)

        time_list = [sheet.cell(i, 2).value for i in range(day_coordinates[0], day_coordinates[0] + day_height)]
        lessons_list = [sheet.cell(i, group_num + 2).value for i in range(day_coordinates[0],
                                                                          day_coordinates[0] + day_height)]
        # Reduction
        lessons_list = list(map(lambda x: x.replace('Физическая культура и спорт (Элективные дисциплины) (СПЗ)',
                                                    'Физическая культура (Лекция) (СПЗ)').replace(
                                                    'Вычислительные системы, сети и телекоммуникации',
                                                    'Вычислительные системы').replace(
                                                    'Алгоритмизация и программирование',
                                                    'Алгоритмизация'), lessons_list))

        return [f'Группа №{group_num} ' + week[num_of_day_of_week], ''] + time_list, ['', ''] + lessons_list

    # get_coordinates_by_value------------------------------------------------------------------------------------------
    @staticmethod
    def __find_ceil_coordinates(sheet, target):
        for j in range(sheet.ncols):
            for i in range(sheet.nrows):
                if str(sheet.cell(i, j).value).lower() == target.lower():
                    return i, j
        return i, j

    # get_height--------------------------------------------------------------------------------------------------------
    @staticmethod
    def __get_height_of_day_of_week(sheet, coordinates):
        x = coordinates[0] + 1
        y = coordinates[1]
        out = 1
        for i in range(x, sheet.nrows):
            if sheet.cell(x, y).value == '':
                x += 1
                out += 1
            else:
                return out
        return out

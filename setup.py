# Импорт библиотек
# Создание графического интерфейса
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning, askyesno
from tkinter.simpledialog import askinteger, askstring

# Работа с файлами
import os
import shutil
from glob import glob
from pathvalidate import sanitize_filename

# Работа со списками
import numpy

# Управление
from keyboard import is_pressed, add_hotkey

# Монте Карло
from random import randint, choice


# Выбирает наиболее подходящий цвет для текста в зависимости от фона
def chooseColor(hex):
    color = hex.lstrip('#')
    lv = len(color)
    rgb = tuple(int(color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    if (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114) > 186:
        return 'black'
    return 'white'


# Склонение слов
def declination(n=0, words=('секунду', 'секунды', 'секунд')):
    n = str(n)
    if n != '11' and n[-1] == '1':
        return words[0]
    if n[0] != '1' and n[-1] in '234':
        return words[1]
    return words[2]


# Основная программа
class SetUp:
    # Инициализация (подготовка к работе)
    def __init__(self):
        # Создание окна
        self.root = tk.Tk()  # Окно
        self.root.resizable(False, False)  # Отключение возможности изменения размера
        self.root.title('Инициализация')  # Оглавление
        self.root['bg'] = '#000000'  # Цвет

        # Загрузочный лейбл
        load = tk.Label(self.root, text='Ожидание окончания инициализации...', font=('Helvetica', '30'))  # Лейбл
        load.grid()  # Отрисовка
        self.root.update()  # Обновление окна

        # Лимиты значений высоты
        self.minlimit = -1  # Минимальный
        self.maxlimit = 9  # Максимальный
        self.limitLength = self.maxlimit - self.minlimit + 1  # Нахождение разницы между лимитами

        # Загрузка диапазона
        self.loadRange()

        # Файлы для конфигураций
        self.configFiles = ('colors.txt', 'range.txt', 'map.txt')

        # Управление ЛКМ
        # Клавиши для вывода
        self.hotkeys = [y for y in list(range(1, 10))]  # Создание списка со значениями от 1 до 9
        self.hotkeys.extend([0, -1])  # Добавление значений 0 и -1
        # Клавиши для распознавания
        self.keys = [y for y in list(range(2, 12))]  # Создание списка со значениями от 2 до 11
        self.keys.append('-')  # Добавление значения '-'

        add_hotkey('Esc', self.switch)

        # Цвета, использующиеся для кнопок [Можно легко изменять]
        button_colors = {
            # Текст
            'foreground': (
                '#000000',  # Стандартный

                '#082f17',  # Запуск
                '#400820'  # Выход
            ),
            # Текст при нажатии
            'activeforeground': (
                '#ef9200',  # Изменить количество строк/столбцов
                '#0075b7',  # Изменить карту/цвет
                '#324b21',  # Сохранить текущую конфигурацию
                '#00747e',  # Загрузить конфигурацию
                '#3c178f',  # Построение плотин с помощью Монте Карло

                '#167c3e',  # Запуск
                '#91193e'  # Выход
            ),
            # Задний фон
            'background': (
                '#b2b2b2',  # Стандартный

                '#167c3e',  # Запуск
                '#91193e'  # Выход
            ),
            # Задний фон при нажатии
            'activebackground': (
                '#ffe79d',  # Изменить количество строк/столбцов
                '#6ecaff',  # Изменить карту/цвет
                '#abff74',  # Сохранить текущую конфигурацию
                '#75f3ff',  # Загрузить конфигурацию
                '#8a66dc',  # Построение плотин с помощью Монте Карло

                '#55c882',  # Запуск
                '#dd5c84'  # Выход
            )
        }

        # Изменить количество строк
        self.getrow = tk.Button(
            text=f'Изменить количество строк [{self.range[0]}]',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][0],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][0],
            overrelief='flat',
            command=lambda: self.getRowCol(False)
        )
        self.getrow.bind('<Button-3>', lambda event: self.getRowCol(column=False, rightClick=True))

        # Изменить количество столбцов
        self.getcol = tk.Button(
            text=f'Изменить количество столбцов [{self.range[1]}]',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][0],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][0],
            overrelief='flat',
            command=lambda: self.getRowCol(True)
        )
        self.getcol.bind('<Button-3>', lambda event: self.getRowCol(column=True, rightClick=True))

        # Изменить карту
        getmap = tk.Button(
            text='Изменить карту',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][1],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][1],
            overrelief='flat',
            command=self.getMap
        )
        # Сбросить карту
        getmap.bind('<Button-3>', self.resetMap)

        # Изменить цвет
        getcolor = tk.Button(
            text='Изменить цвет',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][1],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][1],
            overrelief='flat',
            command=self.getColor
        )
        # Сбросить цвет
        getcolor.bind('<Button-3>', self.resetColor)

        # Сохранить текущую конфигурацию
        saveconfig = tk.Button(
            text='Сохранить текущую конфигурацию',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][2],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][2],
            overrelief='flat',
            command=self.saveConfiguration
        )

        # Загрузить конфигурацию
        loadconfig = tk.Button(
            text='Загрузить конфигурацию',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][3],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][3],
            overrelief='flat',
            command=self.loadConfigurations
        )

        # Построение плотин с помощью Монте Карло
        montecarlo = tk.Button(
            text='Построение плотин с помощью Монте Карло',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][0],
            activeforeground=button_colors['activeforeground'][4],
            bg=button_colors['background'][0],
            activebackground=button_colors['activebackground'][4],
            overrelief='flat',
            command=self.startMonteCarlo
        )

        # Запуск
        self.launch = tk.Button(
            text='Запустить программу [Запуск]',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][1],
            activeforeground=button_colors['activeforeground'][5],
            bg=button_colors['background'][1],
            activebackground=button_colors['activebackground'][5],
            overrelief='flat',
            command=self.launchProgram
        )

        # Выход
        stop = tk.Button(
            text='Завершить настройку [Выход]',
            font=('Helvetica', '20'),
            fg=button_colors['foreground'][2],
            activeforeground=button_colors['activeforeground'][6],
            bg=button_colors['background'][2],
            activebackground=button_colors['activebackground'][6],
            overrelief='flat',
            command=self.root.destroy
        )

        # Уничтожение загрузочного лейбла
        load.destroy()

        # Отрисовка всех кнопок
        self.getrow.grid(rowspan=2, padx=3, pady=3, sticky='nesw')  # Изменить количество строк
        self.getcol.grid(row=1, column=1, padx=3, pady=3, sticky='nesw')  # Изменить количество столбцов
        getmap.grid(row=2, padx=3, pady=3, sticky='nesw')  # Изменить карту
        getcolor.grid(row=2, column=1, padx=3, pady=3, sticky='nesw')  # Изменить цвет
        saveconfig.grid(row=3, padx=3, pady=3, sticky='nesw')  # Сохранить текущую конфигурацию
        loadconfig.grid(row=3, column=1, padx=3, pady=3, sticky='nesw')  # Загрузить конфигурацию
        montecarlo.grid(row=4, columnspan=2, padx=3, pady=3, sticky='nesw')
        self.launch.grid(row=5, columnspan=2, padx=3, pady=3, sticky='nesw')  # Запуск
        stop.grid(row=6, columnspan=2, padx=3, pady=3, sticky='nesw')  # Выход

        # Завершение инициализации
        self.root.title('Настройка программы')  # Оглавление
        self.root.mainloop()  # Ожидание закрытия окна

    # Изменить количество строк/столбцов
    def getRowCol(self, column=False, rightClick=False):
        # Сброс при зажатой клавише Ctrl или при нажатии ПКМ
        if is_pressed('Ctrl') or rightClick:
            requested_variable = 10
        # Иначе запрос количества строк/столбцов
        else:
            # Запрос в зависимости от требуемого параметра
            prompt = ('Количество строк:', 'Количество столбцов:')[column]

            # Цикл запроса
            while True:
                # Запрос параметра
                requested_variable = askinteger(title='Настройка программы', prompt=prompt)
                # Если запрос отменен - вернуться
                if requested_variable is None:
                    return
                # Если введенное значение совпадает с необходимыми условиями (больше нуля) - завершить запрос
                if requested_variable > 0:
                    break
                # Иначе вывод предупреждения об условии
                showwarning('Недопустимое значение', 'Требуется ввести значение больше нуля')

        # Объявление защитной переменной [Предохраняемся! :D]
        # Переменная принимает значение меньшего из прошлого значения и введенного
        protection = min(self.range[column], requested_variable)

        # Прошлое значение принимает вид нового
        self.range[column] = requested_variable

        # Создание новой карты
        newmap = numpy.zeros(self.range, dtype=object).tolist()

        # Значения для проведения вычислительных процессов в зависимости от требуемого параметра
        variables = (
            (protection, self.range[1], protection, self.range[0], self.range[1]),
            (self.range[0], protection, self.range[0], protection, self.range[1])
        )[column]

        # Обновление карты
        self.loadMap()

        # Запись текущей карты в новую
        # Индексы строк принимают либо минимальные значения, либо введенные в зависимости от требуемого параметра
        for i in range(variables[0]):
            # Индексы столбцов принимают либо введенные значения, либо минимальные в зависимости от требуемого параметра
            for j in range(variables[1]):
                newmap[i][j] = self.map[i][j]

        # Можно убрать из комментариев, если требуется изменить начальное значение
        # для новых клеток с нуля до другого значения, и изменить цифру для приравнивания новой карты
        '''
        # # Расширение/уменьшение карты в зависимости от изменения количества строк/столбцов
        # # Если требуемый параметр - строка
        if not column:
            # Индексы строки расставляются от наименьшего значения до введенного
            for i in range(variables[2], variables[3]):
                for j in range(variables[4]):
                    newmap[i][j] = 0  # <- Цифра для приравнивания
        # Иначе, если требуемый параметр - столбец
        elif column:
            for i in range(variables[2]):
                # Индексы столбцов расставляются от наименьшего значения до введенного
                for j in range(variables[3], variables[4]):
                    newmap[i][j] = 0  # <- Цифра для приравнивания
        '''

        # Создание новой карты
        self.map = numpy.zeros(self.range, dtype=object).tolist()
        # Запись в карту значений с новой карты
        for i in range(self.range[0]):
            for j in range(self.range[1]):
                self.map[i][j] = newmap[i][j]
        # Запись новой карты в файл [Примечание: карта используется в двоичном режиме]
        open('map.txt', 'w', encoding='utf-8').write(str(self.map))

        # Запись нового диапазона в файл
        open('range.txt', 'w', encoding='utf-8').write('\n'.join(map(str, self.range)))
        # Если запрашиваемый параметр - строка, то обновить текст у соответствующей кнопки
        if not column:
            self.getrow.configure(text=f'Изменить количество строк [{self.range[0]}]')
        # Иначе, если запрашиваемый параметр - столбец, то обновить текст у другой кнопки
        elif column:
            self.getcol.configure(text=f'Изменить количество столбцов [{self.range[1]}]')

        # Возвращает введенное значение
        return requested_variable

    # Обработка нажатия на кнопку
    def on_click_button(self, i=0, j=0, rightClick=False):
        # Обработка нажатых клавиш
        l = list(is_pressed(x) for x in self.keys)
        # Если какая-либо клавиша нажата, то записываем соответствующее значение кнопки
        if True in l:
            value = self.hotkeys[l.index(True)]

        # Иначе, если нажата клавиша Ctrl или была использована ПКМ
        elif is_pressed('Ctrl') or rightClick:
            # Уменьшение значения кнопки на 1 с обработкой возможности выйти за границы
            value = self.newmap[i][j] - 1
            if value < self.minlimit:
                value = self.maxlimit
        # Иначе увеличить значение кнопки на 1 с обработкой возможности выйти за границы
        else:
            value = self.newmap[i][j] + 1
            if value > self.maxlimit:
                value = self.minlimit
        # Изменение значения клетки у новой карты
        self.newmap[i][j] = value
        # Обработка необходимых цветов для кнопки
        background = self.colors[value]  # Задний фон
        foreground = self.colors1[background]  # Текст
        # Изменение свойств кнопки
        self.b[i][j].configure(
            text=value, bg=background, fg=foreground, activebackground=foreground, activeforeground=background
        )

    # Сохранение карты
    def saveMap(self):
        # Запись новой карты в файл
        open('map.txt', 'w', encoding='utf-8').write(str(self.newmap))
        # Запись в карту значений с новой карты
        for i in range(self.range[0]):
            for j in range(self.range[1]):
                self.map[i][j] = self.newmap[i][j]
        # Уничтожение окна с изменением карты
        self.mapwin.destroy()
        # Вывод информации об успешном сохранении новой карты
        showinfo('Сохранение', 'Карта успешно сохранена')

    # Изменить карту
    def getMap(self):
        # Обновление параметров
        self.loadRange()  # Диапазон
        self.loadColor()  # Цвет
        self.loadMap()  # Карта

        # Создание списков кнопок и новой карты
        self.b = numpy.zeros(self.range, dtype=object).tolist()
        self.newmap = numpy.zeros(self.range, dtype=object).tolist()

        # Создание окна изменения карты
        self.mapwin = tk.Toplevel(self.root)  # Окно
        self.mapwin.resizable(False, False)  # Отключение возможности изменения размера окна
        self.mapwin.title('Карта')  # Оглавление

        # Циклы создания кнопок
        for i in range(self.range[0]):
            for j in range(self.range[1]):
                # Запись в новую карту текущую карту
                value = self.newmap[i][j] = self.map[i][j]
                # Применение цветов для кнопки
                background = self.colors[value]  # Задний фон
                foreground = self.colors1[background]  # Текст
                # Создание кнопки с необходимыми параметрами
                self.b[i][j] = tk.Button(
                    self.mapwin, text=value, width=3, height=1, bg=background, fg=foreground,
                    activebackground=foreground, activeforeground=background, font=('Helvetica', '20'),
                    command=lambda x=i, y=j: self.on_click_button(x, y)
                )
                self.b[i][j].bind('<Button-3>', lambda event, x=i, y=j: self.on_click_button(x, y, rightClick=True))
                # Отрисовка
                self.b[i][j].grid(row=i, column=j)

        # Создание кнопки Сохранить
        save = tk.Button(
            self.mapwin, text='Сохранить', font=('Helvetica', '20'), bg='#471F9C', fg='white',
            activebackground='#8751D4', activeforeground='#220C40', overrelief='flat', command=self.saveMap
        )

        # Создание кнопки Отмена
        cancel = tk.Button(
            self.mapwin, text='Отмена', font=('Helvetica', '20'), bg='#91193e', fg='white', activebackground='#c42254',
            activeforeground='#440b1d', overrelief='flat', command=self.mapwin.destroy
        )

        # Вычисление значения для корректного размещения кнопок
        span = self.range[1] // 2
        if self.range[1] % 2 == 1:
            span += 1

        # Отрисовка кнопок
        save.grid(row=self.range[0], columnspan=span, sticky='nesw')
        cancel.grid(row=self.range[0], column=span, columnspan=span, sticky='nesw')

    # Сбросить карту
    def resetMap(self, info=True):
        # Если нужна информация и пользователь отвергает подтверждение, то вернуться
        if info and not askyesno('Сброс карты', 'Вы действительно хотите выполнить сброс карты?'):
            return
        # Иначе пересоздание карты
        self.map = numpy.zeros(self.range, dtype=object).tolist()
        # Запись карты в файл
        open('map.txt', 'w', encoding='utf-8').write(str(self.map))
        # Если нужна информация, то вывести сообщение об успешном сбросе карты
        if info:
            showinfo('Сброс', 'Карта успешно сброшена')

    # Проверка цвета
    def checkColor(self):
        # Создание окна для проверки цвета
        checkwin = tk.Tk()  # Окно
        checkwin.withdraw()  # Скрытие

        # Создание списка для хранения обновленных цветов
        resultColors = [''] * self.limitLength
        # Переменная для определения ошибки
        allRight = True
        # Цикл проверки цветов
        for i in range(self.limitLength):
            # Получение цвета в поле ввода
            inputColor = self.e[i].get()
            # Переменная для определения ошибки в текущем цвете
            correct = True
            # Попробовать применить цвет
            try:
                tk.Label(checkwin, fg=inputColor)
            # Если возникла проблема, то...
            except:
                # Попробовать применить цвет с символом '#'
                try:
                    inputColor = '#' + inputColor
                    tk.Label(checkwin, fg=inputColor)
                # Если возникла проблема, то указать на ошибку и присвоить переменным статус ошибки
                except:
                    self.e[i].focus()
                    allRight = correct = False
            # Если цвет верный, то записать его в список
            if correct:
                resultColors[i] = inputColor
        # Если все верно, то уничтожить окно изменения цвета, записать обновленные цвета в файл
        # и показать сообщение об успешном изменении цвета
        if allRight:
            self.colorwin.destroy()
            open('colors.txt', 'w', encoding='utf-8').write('\n'.join(x for x in resultColors))
            showinfo('Изменение', 'Цвет успешно изменён')
        # Иначе показать предупреждение о несуществующем цвете
        else:
            showwarning('Недопустимое значение', 'Введите существующий цвет в виде слова или HEX-кода')
        # Уничтожить окно проверки цвета
        checkwin.destroy()

    # Изменить цвет
    def changeColor(self, i):
        # Получение цвета с поля ввода
        inputColor = self.e[i].get()
        # Попробовать очистить текст и применить цвет к лейблу и изменить цвет поля ввода на белый
        try:
            self.colorBox[i].configure(text='', bg=inputColor)
            self.e[i].configure(bg='white')
        # Если возникла проблема, то...
        except:
            # Попробовать очистить текст и применить цвет к лейблу с символом '#' и изменить цвет поля ввода на белый
            try:
                inputColor = '#' + inputColor
                self.colorBox[i].configure(text='', bg=inputColor)
                self.e[i].configure(bg='white')
            # Если возникал проблема, то изменить лейбл в соответствии с ситуацией и применить красный цвет к полю ввода
            except:
                self.colorBox[i].configure(text='None', bg='black')
                self.e[i].configure(bg='red')

    # Изменить цвет
    def getColor(self):
        # Создание окна изменения цвета
        self.colorwin = tk.Toplevel(self.root)  # Окно
        self.colorwin.resizable(False, False)  # Запрет изменения размера окна
        self.colorwin.title('Изменение цвета')  # Оглавление

        # Загрузка цветов из файла
        colorValues = open('colors.txt', 'r', encoding='utf-8').read().split('\n')
        # Создание списка доступных уровней
        colorLevels = list(range(self.minlimit, self.maxlimit + 1))
        # Создание списка для хранения текста (лейблов)
        l = [0] * self.limitLength
        # Создание списка для хранения цветных лейблов
        self.colorBox = [0] * self.limitLength
        # Создание списка для хранения полей ввода
        self.e = [0] * self.limitLength
        # Цикл заполнения списков
        for i in range(self.limitLength):
            # Заполнение текста
            l[i] = tk.Label(self.colorwin, text=f'Цвет [{colorLevels[i]}]:', font=('Helvetica', '15'))
            # Заполнение цветных лейблов
            self.colorBox[i] = tk.Label(
                self.colorwin, font=('Helvetica', '10', 'bold'), fg='white', bg=colorValues[i], width=4, height=2
            )
            # Добавление StringVar для получения начального текста в полях ввода
            var = tk.StringVar(self.colorwin, value=colorValues[i])
            # Заполнение полей ввода
            self.e[i] = tk.Entry(self.colorwin, textvariable=var, font=('Helvetica', '15'), width=12)
            # Назначение команды на отпускание клавиши
            self.e[i].bind('<KeyRelease>', lambda event, x=i: self.changeColor(x))

            # Отрисовка
            l[i].grid(padx=5, pady=5)  # Текст
            self.colorBox[i].grid(row=i, column=1, padx=5, pady=5)  # Цветные лейблы
            self.e[i].grid(row=i, column=2, padx=5, pady=5)  # Поля ввода

        # Создание кнопки Сохранить
        apply = tk.Button(self.colorwin, text='Сохранить', font=('Helvetica', '15'), command=self.checkColor)
        # Создание кнопки Отмена
        cancel = tk.Button(self.colorwin, text='Отмена', font=('Helvetica', '15'), command=self.colorwin.destroy)

        # Отрисовка
        apply.grid(columnspan=2, padx=5, pady=5, sticky='nesw')  # Кнопка Применить
        cancel.grid(row=i+1, column=2, padx=5, pady=5, sticky='nesw')  # Кнопка Отмена

        # Ожидание закрытия окна
        self.colorwin.mainloop()

    # Сбросить цвет
    def resetColor(self, info=True):
        # Если требуется информация и пользователь отклоняет подтверждение сброса цвета, то вернуться
        if info and not askyesno('Сброс цвета', 'Вы действительно хотите выполнить сброс цвета?'):
            return
        # Цвета
        self.colors = {
            -1: '#0000f0',
            0: '#bc8f8f',
            1: '#f4a460',
            2: '#daa520',
            3: '#b8860b',
            4: '#cd853f',
            5: '#d2691e',
            6: '#8b4513',
            7: '#a0522d',
            8: '#a52a2a',
            9: '#800000',
        }
        # Запись цветов в файл
        open('colors.txt', 'w', encoding='utf-8').write('\n'.join(x for x in self.colors.values()))
        # Если требуется информация, то вывести сообщение об успешном сбросе цвета
        if info:
            showinfo('Сброс', 'Цвет успешно сброшен')

    # Сохранить текущую конфигурацию
    def saveConfiguration(self):
        # Цикл запроса имени конфигурации
        while True:
            # Запрос
            configName = askstring(title='Сохранение', prompt='Выберите имя для конфигурации:')
            # Если пользователь отменил запрос, то вернуться
            if configName is None:
                return
            configName = sanitize_filename(configName)
            if configName in {''}:
                showwarning(
                    'Недопустимое значение',
                    'Введено недопустимое имя конфигурации.\n\n'
                    'Выберите другое имя'
                )
                continue
            # Иначе, если введенная конфигурация уже существует
            # и пользователь не подтверждает замену, то продолжить запрос
            if os.path.exists(f'Configurations\\{configName}') and not askyesno(
                    'Конфигурация существует', 'Конфигурация с таким именем уже есть\n\nВы желаете её заменить?'
            ):
                continue
            if askyesno(
                    'Подтверждение',
                    f'Будет создана конфигурация\n[{configName}]\n\nВы подтверждаете сохранение конфигурации?'
            ):
                # Завершить запрос
                break
        # Если папка с конфигурациями отсутствует, то создать её
        if not os.path.exists('Configurations'):
            os.mkdir('Configurations')
        # Переменная для хранения пути до конфигурации
        configPath = f'Configurations\\{configName}'
        # Если папки конфигурации не существует, то создать её
        if not os.path.exists(configPath):
            os.mkdir(configPath)
        # Обновление параметров
        self.loadRange()  # Диапазон
        self.loadColor()  # Цвет
        self.loadMap()  # Карта
        # Цикл копирования файлов
        for file in self.configFiles:
            # Копирование текущих настроек в папку с конфигурацией
            shutil.copyfile(file, f'{configPath}\\{file}')
        # Вывод сообщения об успешном сохранении конфигурации
        showinfo('Сохранение', 'Конфигурация успешно сохранена')

    # Применение конфигурации
    def applyConfiguration(self):
        AltIsNotPressed = not is_pressed('Alt')
        if AltIsNotPressed:
            # Если пользователь отвергнул подтверждение загрузки конфигурации, то вернуться
            if not askyesno('Внимание!', 'Загрузка конфигурации приведёт к потере текущих настроек\n\nВы подтверждаете загрузку конфигурации?'):
                return
        # Получение имени выбранной к применению конфигурации
        configName = self.combobox.get()
        # Уничтожение окна загрузки конфигурации
        self.configwin.destroy()
        # Запись пути конфигурации в переменную
        configPath = f'Configurations\\{configName}'
        # Цикл проверки конфигурации
        for file in self.configFiles:
            # Если в конфигурации нет запрашиваемого файла, то предложить удалить конфигурацию и вернуться
            if not os.path.exists(f'{configPath}\\{file}'):
                if askyesno(
                    'Ошибка конфигурации',
                    'Кажется, запрашиваемая конфигурация неполноценна/повреждена.\n'
                    'Продолжение текущей операции недопустимо\n\n'
                    'Вы желаете удалить эту конфигурацию?'
                ):
                    shutil.rmtree(configPath, ignore_errors=True)
                    showinfo('Удаление', 'Конфигурация успешно удалена')
                elif is_pressed('Alt'):
                    break
                return
        # Цикл применения конфигурации
        for file in self.configFiles:
            # Копирование файла из папки конфигурации к текущим файлам
            if os.path.exists(f'{configPath}\\{file}'):
                shutil.copyfile(f'{configPath}\\{file}', file)
        # Загрузка диапазона
        self.loadRange()
        if AltIsNotPressed:
            # Показ сообщения об успешной загрузке конфигурации
            showinfo('Загрузка', 'Конфигурация успешно загружена')

    # Загрузить конфигурацию
    def loadConfigurations(self):
        configurations = tuple(x for x in glob('Configurations\*'))
        IsNotDir = tuple(x for x in configurations if not os.path.isdir(x))
        if len(IsNotDir) > 0:
            txt = (('Посторонние файлы', 'обнаружены посторонние файлы', 'их', 'Файлы успешно удалены'),
                   ('Посторонний файл', 'обнаружен посторонний файл', 'его', 'Файл успешно удален')
                   )[len(IsNotDir) == 1]
            if askyesno(txt[0], f'В папке конфигураций {txt[1]}\n\nВы желаете {txt[2]} удалить?'):
                for file in IsNotDir:
                    os.remove(file)
                showinfo('Удаление', txt[3])
        # Получение кортежа конфигураций
        configurations = tuple(x.replace('Configurations\\', '') for x in configurations if os.path.isdir(x))
        # Получение количества конфигураций
        configLength = len(configurations)
        # Если нет сохранённых конфигураций, то показать сообщение об этом и вернуться
        if configLength == 0:
            showinfo('Конфигурация', 'Нет сохранённых конфигураций')
            return

        # Создание окна загрузки конфигурации
        self.configwin = tk.Toplevel(self.root)  # Окно
        self.configwin.resizable(False, False)  # Запрет изменения размера окна
        self.configwin.title('Загрузка конфигурации')  # Оглавление

        # Выравнивание окна по центру экрана
        width = 505  # Ширина окна
        height = 130  # Высота окна
        screenWidth = self.configwin.winfo_screenwidth()  # Ширина экрана
        screenHeight = self.configwin.winfo_screenheight()  # Высота экрана
        x = screenWidth/2 - width/2  # Получение середины ширины окна
        y = screenHeight/2 - height/2  # Получение середины высоты окна
        self.configwin.geometry('%dx%d+%d+%d' % (width, height, x, y))  # Применение настроек для выравнивания окна

        # Получение текста количества доступных конфигураций
        configAvailable = declination(
            configLength, ('Доступна %s конфигурация', 'Доступно %s конфигурации', 'Доступно %s конфигураций')
        ) % configLength
        # Создание лейбла количества конфигураций
        configAvailableLabel = tk.Label(self.configwin, text=configAvailable, font=('Helvetica', '15'))
        # Создание лейбла загрузки конфигурации
        loadConfig = tk.Label(self.configwin, text='Загрузить конфигурацию:', font=('Helvetica', '15'))

        # Создание выпадающего списка и выбор первого значения в нём
        self.combobox = ttk.Combobox(self.configwin, font=('Helvetica', '15'), values=configurations, state='readonly')
        self.combobox.current(0)

        # Создание кнопки Загрузить
        load = tk.Button(self.configwin, text='Загрузить', font=('Helvetica', '15'), command=self.applyConfiguration)
        # Создание кнопки Отмена
        cancel = tk.Button(self.configwin, text='Отмена', font=('Helvetica', '15'), command=self.configwin.destroy)

        # Отрисовка всех элементов
        configAvailableLabel.grid(columnspan=2, padx=5, pady=5)  # Количество конфигураций
        loadConfig.grid(padx=5, pady=5)  # Загрузить конфигурацию
        self.combobox.grid(row=1, column=1, padx=5, pady=5)  # Выпадающий список конфигураций
        load.grid(padx=5, pady=5, sticky='nesw')  # Кнопка Загрузить
        cancel.grid(row=2, column=1, padx=5, pady=5, sticky='nesw')  # Кнопка Отмена

        # Ожидание закрытия окна
        self.configwin.mainloop()

    def switch(self):
        self.stop = True

    def countWater(self, mapter, info=True):
        water = 0
        for i in range(self.range[0]):
            for j in range(self.range[1]):
                water += mapter[i][j] == -1
        # open('results.txt', 'w', encoding='utf-8').write(str(water))
        if info:
            showinfo('Результат', f'Клеток с водой: {water}')
        return water

    def floodProgram(self, h, itr, StandartUsage=True, info=True, mainloop=False, inputmap=None):
        if StandartUsage:
            flood = tk.Toplevel(self.root)
            flood.resizable(False, False)
            flood.title('Потоп')

            self.stop = False

        self.loadRange()
        self.loadColor()
        self.loadMap()
        n, m = self.range
        mapter = numpy.zeros(self.range, dtype=object).tolist()
        mapnew = numpy.zeros(self.range, dtype=object).tolist()

        if type(inputmap) == list:
            for i in range(n):
                for j in range(m):
                    mapter[i][j] = inputmap[i][j]
                    mapnew[i][j] = inputmap[i][j]
        else:
            for i in range(n):
                for j in range(m):
                    mapter[i][j] = self.map[i][j]
                    mapnew[i][j] = self.map[i][j]

        water = self.countWater(mapter, info=False)

        # Пробегаемся по итерациям наводнения
        for it in range(itr):
            for i in range(1, n - 1):
                for j in range(1, m - 1):
                    if mapter[i][j] <= h and (
                            mapter[i - 1][j - 1] == -1 or mapter[i - 1][j] == -1 or mapter[i - 1][j + 1] == -1
                            or mapter[i][j - 1] == -1 or mapter[i][j + 1] == -1 or mapter[i + 1][j - 1] == -1
                            or mapter[i + 1][j] == -1 or mapter[i + 1][j + 1] == -1
                    ):
                        mapnew[i][j] = -1

            for i in range(1, n - 1):
                if mapter[i][0] <= h and (mapter[i - 1][0] == -1 or mapter[i][1] == -1 or mapter[i + 1][0] == -1):
                    mapnew[i][0] = -1
                if mapter[i][m - 1] <= h and (
                        mapter[i - 1][m - 1] == -1 or mapter[i][m - 2] == -1 or mapter[i + 1][m - 1] == -1):
                    mapnew[i][m - 1] = -1

            for j in range(1, m - 1):
                if mapter[0][j] <= h and (mapter[0][j - 1] == -1 or mapter[1][j] == -1 or mapter[0][j + 1] == -1):
                    mapnew[0][j] = -1
                if mapter[n - 1][j] <= h and (
                        mapter[n - 1][j - 1] == -1 or mapter[n - 2][j] == -1 or mapter[n - 1][j + 1] == -1):
                    mapnew[n - 1][j] = -1

            if mapter[0][0] <= h and (mapter[0][1] == -1 or mapter[1][0] == -1):
                mapnew[0][0] = -1
            if mapter[0][m - 1] <= h and (mapter[0][m - 2] == -1 or mapter[1][m - 1] == -1):
                mapnew[0][m - 1] = -1
            if mapter[n - 1][0] <= h and (mapter[n - 1][1] == -1 or mapter[n - 2][0] == -1):
                mapnew[n - 1][0] = -1
            if mapter[n - 1][m - 1] <= h and (mapter[n - 1][m - 2] == -1 or mapter[n - 2][m - 1] == -1):
                mapnew[n - 1][m - 1] = -1

            l = numpy.zeros(self.range, dtype=object).tolist()
            if StandartUsage:
                for i in range(n):
                    for j in range(m):
                        mapter[i][j] = int(mapnew[i][j])

                        value = mapter[i][j]
                        background = self.colors[value]
                        foreground = self.colors1[background]

                        l[i][j] = tk.Label(
                            flood,
                            text=value, fg=foreground, font=('Helvetica', '14'), bg=background, width=6, height=3,
                            borderwidth=1, relief='raised'
                        )
                        l[i][j].grid(row=i, column=j)

                flood.update()
                waternew = self.countWater(mapter, info=False)
                if self.stop or water == waternew:
                    break
                water = waternew

            else:
                for i in range(n):
                    for j in range(m):
                        mapter[i][j] = int(mapnew[i][j])

        water = self.countWater(mapter, info=info)
        if StandartUsage:
            if mainloop:
                flood.mainloop()
            else:
                flood.destroy()
        return water

    # Запуск
    def launchProgram(self):
        # Скрытие корневого окна
        self.root.withdraw()
        # Запуск программы
        h = askinteger('Уровень затопления', 'Уровень затопления:')
        if h is None:
            self.root.deiconify()
            return
        itr = askinteger('Итерации', 'Итерации:')
        if itr is None:
            self.root.deiconify()
            return
        self.root.deiconify()
        self.floodProgram(h, itr)

    # Монте Карло
    def startMonteCarlo(self):
        self.settings = tk.Toplevel(self.root)
        self.settings.resizable(False, False)
        self.settings.title('Настройка')

        self.iterationsLabel = tk.Label(self.settings, text='Итерации:', font=('Helvetica', '20'))
        self.iterationsSpinbox = tk.Spinbox(
            self.settings,
            values=('1000', '3000', '5000', '10000'),
            wrap=True, font=('Helvetica', '20')
        )

        self.heigthWaterLabel = tk.Label(self.settings, text='Высота воды:', font=('Helvetica', '20'))
        var = tk.StringVar(self.settings, value='8')
        self.heigthWaterSpinbox = tk.Spinbox(
            self.settings, from_=0, to=8, textvariable=var, wrap=True, font=('Helvetica', '20')
        )

        self.amountPlotLabel = tk.Label(self.settings, text='Количество плотин:', font=('Helvetica', '20'))
        self.amountPlotSpinbox = tk.Spinbox(self.settings, from_=1, to=10, wrap=True, font=('Helvetica', '20'),)

        self.heigthPlotLabel = tk.Label(self.settings, text='Высота плотин:', font=('Helvetica', '20'))
        var = tk.StringVar(self.settings, value='9')
        self.heigthPlotSpinbox = tk.Spinbox(
            self.settings, from_=1, to=9, textvariable=var, wrap=True, font=('Helvetica', '20')
        )

        apply = tk.Button(self.settings, text='Продолжить', font=('Helvetica', '20'), command=self.MonteCarlo)

        cancel = tk.Button(self.settings, text='Отмена', font=('Helvetica', '20'), command=self.settings.destroy)


        self.iterationsLabel.grid(padx=3, pady=3, sticky='w')
        self.iterationsSpinbox.grid(padx=3, pady=3)

        self.heigthWaterLabel.grid(row=0, column=1, padx=3, pady=3, sticky='w')
        self.heigthWaterSpinbox.grid(row=1, column=1, padx=3, pady=3)

        self.amountPlotLabel.grid(padx=3, pady=3, sticky='w')
        self.amountPlotSpinbox.grid(padx=3, pady=3)

        self.heigthPlotLabel.grid(row=2, column=1, padx=3, pady=3, sticky='w')
        self.heigthPlotSpinbox.grid(row=3, column=1, padx=3, pady=3)

        self.plotTypesLabel = tk.Label(self.settings, text='Виды плотин:', font=('Helvetica', '20'))
        self.plotTypesLabel.grid(padx=3, pady=3, sticky='w')
        self.plotTypes = ['Вертикальный', 'Горизонтальный', 'По диагонали вниз', 'По диагонали вверх']
        self.variables = [0] * len(self.plotTypes)
        for i in range(len(self.plotTypes)):
            self.variables[i] = tk.IntVar(self.settings)
            typeCheckbutton = tk.Checkbutton(
                self.settings, text=self.plotTypes[i], font=('Helvetica', '20'),
                variable=self.variables[i]
            )
            typeCheckbutton.toggle()
            if i % 2 == 0:
                row = 5 + i
                column = 0
            else:
                row = 4 + i
                column = 1
            typeCheckbutton.grid(row=row, column=column, columnspan=2, padx=3, pady=3, sticky='nsw')

        apply.grid(padx=3, pady=3, sticky='nesw')
        cancel.grid(row=4+len(self.plotTypes), column=1, padx=3, pady=3, sticky='nesw')

        self.settings.mainloop()

    def MonteCarlo(self):
        iterations = int(self.iterationsSpinbox.get())
        amountPlot = int(self.amountPlotSpinbox.get())
        hWater = int(self.heigthWaterSpinbox.get())
        if hWater < 0:
            hWater = 0
        elif hWater > 8:
            hWater = 8
        hPlot = int(self.heigthPlotSpinbox.get())
        if hPlot < 1:
            hPlot = 1
        elif hPlot > 9:
            hPlot = 9
        self.variables = [i.get() for i in self.variables]
        if not any(self.variables):
            self.variables[0] = 1
        self.plotTypes = [self.plotTypes[i] for i in range(len(self.plotTypes)) if self.variables[i] == 1]
        self.settings.destroy()

        # Обновление параметров
        self.loadRange()
        self.loadColor()
        self.loadMap()

        # Рассчёт количества клеток на карте
        mapLength = self.range[0] * self.range[1]
        # Создание новой карты
        mapter = numpy.zeros(self.range, dtype=object).tolist()
        bestmap = numpy.zeros(self.range, dtype=object).tolist()

        def newBest():
            print(f'\n***************\nИтерация {it + 1}/{iterations}:')
            for num in range(amountPlot):
                print(f'\nПлотина №{num+1}:')
                print(f'Тип: {typePlot[num]}')
                print(f'Длина: {lengthPlot[num]}')
            print(f'\nВода: {water}/{mapLength}')
            print(f'Затопление: {round(water / mapLength * 100, 2)}%')

        # Запись минимального количества воды
        minwater = mapLength
        typePlot = [''] * amountPlot
        typeChoice = [''] * amountPlot
        lengthPlot = [0] * amountPlot
        lengthChoice = [0] * amountPlot

        for it in range(iterations):

            for i in range(self.range[0]):
                for j in range(self.range[1]):
                    mapter[i][j] = self.map[i][j]

            for plot in range(amountPlot):

                typeChoice[plot] = choice(self.plotTypes)
                lengthChoice[plot] = 0

                if typeChoice[plot] == 'Вертикальный':
                    pj = randint(0, self.range[1] - 1)

                    for i in range(self.range[0]):
                        if mapter[i][pj] == 0:
                            lengthChoice[plot] += 1
                            mapter[i][pj] = hPlot

                elif typeChoice[plot] == 'Горизонтальный':
                    pi = randint(0, self.range[0] - 1)

                    for j in range(self.range[1]):
                        if mapter[pi][j] == 0:
                            lengthChoice[plot] += 1
                            mapter[pi][j] = hPlot

                elif typeChoice[plot] == 'По диагонали вниз':
                    pi = randint(0, self.range[0] - 1)
                    pj = randint(0, self.range[1] - 1)

                    for i in range(min(self.range) - min(pi, pj)):
                        if pi - i < 0 or pj - i <= 0:
                            continue
                        if mapter[pi - i][pj - i] == 0:
                            lengthChoice[plot] += 1
                            mapter[pi - i][pj - i] = hPlot
                        if mapter[pi - i][pj - i - 1] == 0:
                            lengthChoice[plot] += 1
                            mapter[pi - i][pj - i - 1] = hPlot

                elif typeChoice[plot] == 'По диагонали вверх':
                    pi = randint(0, self.range[0] - 1)
                    pj = randint(0, self.range[1] - 1)

                    for i in range(min(self.range) - min(pi, pj)):
                        if pi + i >= self.range[0] or pj - i <= 0:
                            continue
                        if mapter[pi + i][pj - i] == 0:
                            lengthChoice[plot] += 1
                            mapter[pi + i][pj - i] = hPlot
                        if mapter[pi + i][pj - i - 1] == 0:
                            lengthChoice[plot] += 1
                            mapter[pi + i][pj - i - 1] = hPlot

                water = self.floodProgram(hWater, 100, StandartUsage=False, info=False, inputmap=mapter)
                if water < minwater or (water == minwater and lengthChoice[plot] < lengthPlot[plot]):
                    minwater = water
                    for i in range(self.range[0]):
                        for j in range(self.range[1]):
                            bestmap[i][j] = mapter[i][j]
                    typePlot[plot] = typeChoice[plot]
                    lengthPlot[plot] = lengthChoice[plot]
                    newBest()

        for i in range(self.range[0]):
            for j in range(self.range[1]):
                mapter[i][j] = bestmap[i][j]

        self.floodProgram(hWater, 10000, inputmap=mapter, info=False, mainloop=True)

    # Загрузить диапазон
    def loadRange(self):
        # Если файл диапазона существует, то...
        if os.path.exists('range.txt'):
            # Попробовать прочитать его
            try:
                self.range = open('range.txt', 'r', encoding='utf-8').read()
                # Если прочтённая информация пуста, то спровоцировать ошибку
                if self.range == '':
                    0/0
                # Иначе записать обработанную информацию
                self.range = list(map(int, self.range.split('\n')))
            # Если возникла проблема, то выставить значение диапазона Ложь
            except:
                self.range = False

        # Если требуемого пути не существует или значение диапазона равно Ложь,
        # то сбросить диапазон и записать его в файл
        if not os.path.exists('range.txt') or self.range == False:
            open('range.txt', 'w', encoding='utf-8').write('10\n10')
            self.range = [10, 10]
        # Обновление текста у существующих кнопок
        if hasattr(self, 'getrow') and hasattr(self, 'getcol'):
            self.getrow.configure(text=f'Изменить количество строк [{self.range[0]}]')
            self.getcol.configure(text=f'Изменить количество столбцов [{self.range[1]}]')

    # Обновление цветов для текста
    def updateColors1(self):
        # Сброс цветов
        self.colors1 = dict()
        # Цикл заполнения
        for i in self.colors.values():
            # Если цвет не начинается с символа '#'
            if i[0] != '#':
                # Если цвет - белый, то цвет для текста - чёрный
                if i == 'white':
                    self.colors1[i] = 'black'
                # Иначе цвет для текста - белый
                else:
                    self.colors1[i] = 'white'
                # Продолжить выполнение цикла со следующей итерацией
                continue
            # Иначе, цвет для текста определяется функцией
            self.colors1[i] = chooseColor(i)

    # Загрузить цвет
    def loadColor(self):
        # Если файл цвета существует, то...
        if os.path.exists('colors.txt'):
            # Попробовать прочитать информацию
            try:
                self.colors = open('colors.txt', 'r', encoding='utf-8').read()
                # Если информация пуста, то спровоцировать ошибку
                if self.colors == '':
                    0/0
                # Иначе записать обработанную информацию
                self.colors = self.colors.split('\n')
                # Цикл проверки цветов
                for i in self.colors:
                    # Если цвет начинается на символ '#' и его длина меньше 7, то...
                    if i[0] == '#' and len(i) < 7:
                        # Записать индекс цвета
                        index = self.colors.index(i)
                        # Преобразовать цвет в список
                        i = list(i)
                        # Цикл обработки цвета
                        for j in range(2, 7, 2):
                            i.insert(j, '0')
                        # Записать обработанный цвет
                        self.colors[index] = ''.join(i)
                        # Записать цвета в файл
                        open('colors.txt', 'w', encoding='utf-8').write('\n'.join(x for x in self.colors))
                # Преобразовать список цветов в словарь
                self.colors = {x - 1: self.colors[x] for x in range(len(self.colors))}
            # Если возникла проблема, то присвоить цвету значение Ложь
            except:
                self.colors = False
        # Если требуемого пути не существует или значение цвета - Ложь, то сбросить цвет без информации
        if not os.path.exists('colors.txt') or self.colors == False:
            self.resetColor(info=False)
        # Обновить цвета для текста
        self.updateColors1()

    # Загрузить карту
    def loadMap(self):
        # Если путь существует, то...
        if os.path.exists('map.txt'):
            # Попробовать прочитать информацию
            try:
                self.map = eval(open('map.txt', 'r', encoding='utf-8').read())
            # Если возникла проблема, то присвоить карте значение Ложь
            except:
                self.map = False
        # Если требуемого пути не существует или значение карты - Ложь, то сбросить карту без информации
        if not os.path.exists('map.txt') or self.map == False:
            self.resetMap(info=False)


# Если код запущен как программа, а не как модуль
if __name__ == '__main__':
    setup = SetUp()

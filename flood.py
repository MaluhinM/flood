import numpy
import tkinter as tk
from tkinter import simpledialog, messagebox
from os.path import exists
from keyboard import add_hotkey


def countWater():
    water = 0
    for i in range(n):
        for j in range(m):
            water += mapter[i][j] == -1
    # open('results.txt', 'w', encoding='utf-8').write(str(water))
    messagebox.showinfo('Результат', f'Клеток с водой: {water}')

def chooseColor(hex):
    color = hex.lstrip('#')
    lv = len(color)
    rgb = tuple(int(color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    if (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114) > 186:
        return 'black'
    return 'white'


if exists('range.txt'):
    try:
        n, m = map(int, open('range.txt', 'r', encoding='utf-8').read().split('\n'))

    except:
        n = False
if not exists('range.txt') or n == False:
    open('range.txt', 'w', encoding='utf-8').write('10\n10')
    n, m = 10, 10

if exists('colors.txt'):
    try:
        colors = open('colors.txt', 'r', encoding='utf-8').read()
        if colors == '':
            0/0
        colors = colors.split('\n')
        colors = {x-1:colors[x] for x in range(len(colors))}
    except:
        colors = False
if not exists('colors.txt') or colors == False:
    colors = {
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
    open('colors.txt', 'w', encoding='utf-8').write('\n'.join(x for x in colors.values()))

if exists('map.txt'):
    try:
        mapter = eval(open('map.txt', 'r').read())
    except:
        mapter = False
if not exists('map.txt') or mapter == False:
    mapter = numpy.zeros((n, m), dtype=object).tolist()
    for i in range(n):
        for j in range(m):
            mapter[i][j] = 0
    open('map.txt', 'w').write(mapter)

colors1 = dict()
for i in colors.values():
    colors1[i] = chooseColor(i)

mapnew = numpy.zeros((n, m), dtype=object).tolist()

for i in range(n):
    for j in range(m):
        mapter[i][j] = int(mapter[i][j])

for i in range(n):
    for j in range(m):
        mapnew[i][j] = mapter[i][j]

print('\n'.join(map(str, mapter)))

h = simpledialog.askinteger('Уровень затопления', 'Уровень затопления:')
itr = simpledialog.askinteger('Итерации', 'Итерации:')

root = tk.Tk()
root.resizable(False, False)
root.title('Потоп')


def switch():
    global stop
    stop = True


stop = False
add_hotkey('Esc', switch)

# Пробегаемся по итерациям наводнения
for it in range(itr):
    for i in range(1, n-1):
        for j in range(1, m-1):
            if mapter[i][j] <= h and (
                mapter[i - 1][j - 1] == -1 or mapter[i - 1][j] == -1 or mapter[i - 1][j + 1] == -1
                or mapter[i][j - 1] == -1 or mapter[i][j + 1] == -1 or mapter[i + 1][j - 1] == -1
                or mapter[i + 1][j] == -1 or mapter[i + 1][j + 1] == -1
            ):
                mapnew[i][j] = -1

    for i in range(1, n-1):
        if mapter[i][0] <= h and (mapter[i-1][0] == -1 or mapter[i][1] == -1 or mapter[i+1][0] == -1):
            mapnew[i][0] = -1
        if mapter[i][m-1] <= h and (mapter[i-1][m-1] == -1 or mapter[i][m-2] == -1 or mapter[i+1][m-1] == -1):
            mapnew[i][m-1] = -1

    for j in range(1, m-1):
        if mapter[0][j] <= h and (mapter[0][j-1] == -1 or mapter[1][j] == -1 or mapter[0][j+1] == -1):
            mapnew[0][j] = -1
        if mapter[n-1][j] <= h and (mapter[n-1][j-1] == -1 or mapter[n-2][j] == -1 or mapter[n-1][j+1] == -1):
            mapnew[n-1][j] = -1

    if mapter[0][0] <= h and (mapter[0][1] == -1 or mapter[1][0] == -1):
        mapnew[0][0] = -1
    if mapter[0][m-1] <= h and (mapter[0][m-2] == -1 or mapter[1][m-1] == -1):
        mapnew[0][m-1] = -1
    if mapter[n-1][0] <= h and (mapter[n-1][1] == -1 or mapter[n-2][0] == -1):
        mapnew[n-1][0] = -1
    if mapter[n-1][m-1] <= h and (mapter[n-1][m-2] == -1 or mapter[n-2][m-1] == -1):
        mapnew[n-1][m-1] = -1

    l = numpy.zeros((n, m), dtype=object).tolist()
    for i in range(n):
        for j in range(m):
            mapter[i][j] = int(mapnew[i][j])

            value = mapter[i][j]
            background = colors[value]
            foreground = colors1[background]

            l[i][j] = tk.Label(
                text=value, fg=foreground, font=('Helvetica', '13'), bg=background, height=4, width=8,
                borderwidth=1, relief='raised'
            )
            l[i][j].grid(row=i, column=j)
    root.update()
    print()
    print('\n'.join(map(str, numpy.array(mapter).tolist())))
    if stop:
        break

root.mainloop()

countWater()

from random import randint
import time

class BoardException(Exception):
    pass
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"
class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        if self.size == 6 :
            res += "  | 0 | 1 | 2 | 3 | 4 | 5 |"
        else:
            res += "  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |"
        for i, row in enumerate(self.field):
            res += f"\n{i} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    time.sleep(3)
                    return True
                else:
                    print("Корабль ранен!")
                    time.sleep(3)
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        time.sleep(3)
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, num_size - 1), randint(0, num_size - 1))
        print(f"Ход компьютера: {d.x} {d.y}")
        time.sleep(3)
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x, y)

def check_size():
    while True:
        global num_size
        txt_size = input("Введите размер поля для морского боя (6 или 10): ")
        try:
            num_size = int(txt_size)
            if not (num_size == 6 or num_size == 10):
                raise Exception
        except ValueError:
            print("Ошибка! Это не число, попробуйте снова.")
        except Exception:
            print("Введенное число должно быть 6 или 10!")
        else:
            break
    return num_size

class Game:
    def __init__(self, size=check_size()):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True       # ставим параметр False если необходимо увидеть корабли противника на его доске

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        if self.size == 6:
            lens = [3, 2, 2, 1, 1, 1, 1]
        else:
            lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        if num_size == 6:
            print("--------------------")
            print("  Приветствуем вас  ")
            print(" в игре морской бой ")
            print("--------------------")
            print(" Размер поля 6 на 6 ")
            print("--------------------")
            print("  формат ввода: x y ")
            print("  x - номер строки  ")
            print("  y - номер столбца ")
        else:
            print("--------------------------------------------")
            print("     Приветствуем вас в игре морской бой    ")
            print("--------------------------------------------")
            print("        Размер игрового поля 10 на 10       ")
            print("--------------------------------------------")
            print("         формат ввода координат: x y        ")
            print("              x - номер строки              ")
            print("              y - номер столбца             ")

    def loop(self):
        num = 0
        while True:
            if num_size == 6:
                print("-" * 20)
            else:
                print("-" * 44)
            print("Доска пользователя:")
            print(self.us.board)
            if num_size == 6:
                print("-" * 20)
            else:
                print("-" * 44)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                if num_size == 6:
                    print("-" * 20)
                else:
                    print("-" * 44)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                if num_size == 6:
                    print("-" * 20)
                else:
                    print("-" * 44)
                print("Ходит компьютер!")
                time.sleep(3)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                if num_size == 6:
                    print("-" * 20)
                else:
                    print("-" * 44)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == len(self.us.board.ships):
                if num_size == 6:
                    print("-" * 20)
                else:
                    print("-" * 44)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()

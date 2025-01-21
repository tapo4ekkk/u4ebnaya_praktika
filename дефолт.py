import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPainter, QKeyEvent, QPen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class PingPongGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setGeometry(100, 100, 800, 600)

        # Инициализация мяча и ракеток
        self.ball_x = 900
        self.ball_y = 300
        self.ball_dx = 10 * random.choice((1, -1))
        self.ball_dy = 10 * random.choice((1, -1))

        self.left_paddle_y = 250
        self.right_paddle_y = 250

        # Счет
        self.left_score = 0
        self.right_score = 0

        # Таймер и время
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # 60 FPS

        self.elapsed_time = 0  # Время в игре
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Обновление каждую секунду

        # Инициализация и воспроизведение музыки
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("D:\\игра\\Тетрис - Тетрис.mp3")))
        self.player.setVolume(50)  # Уровень громкости (0-100)
        self.player.play()  # Начать воспроизведение

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(Qt.white)

        # Ракетки
        painter.drawRect(50, self.left_paddle_y, 10, 100)  # Левый
        painter.drawRect(1850, self.right_paddle_y, 10, 100)  # Правый

        # Мяч
        painter.drawEllipse(self.ball_x, self.ball_y, 15, 15)

        # Счет
        painter.drawText(900, 50, f"Счет: {self.left_score}  -  {self.right_score}")

        # Время
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        painter.drawText(900, 100, f"Время: {minutes:02}:{seconds:02}")

        # Границы
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawLine(50, 0, 1860, 0)  # Верхняя граница
        painter.drawLine(50, 1000, 1860, 1000)  # Нижняя граница
        painter.drawLine(50, 0, 50, 1000)  # Левая граница
        painter.drawLine(1860, 0, 1860, 1000)  # Правая граница

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_W and self.left_paddle_y > 10:
            self.left_paddle_y -= 20
        elif event.key() == Qt.Key_S and self.left_paddle_y < 890:
            self.left_paddle_y += 20
        elif event.key() == Qt.Key_Up and self.right_paddle_y > 10:
            self.right_paddle_y -= 20
        elif event.key() == Qt.Key_Down and self.right_paddle_y < 890:
            self.right_paddle_y += 20
        self.update()

    def update_game(self):
        # Обновление позиции мяча
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Столкновения с верхом и низом
        if self.ball_y <= 0 or self.ball_y >= 985:
            self.ball_dy *= -1
        
        # Столкновения с ракетками
        if (self.ball_x <= 60 and self.left_paddle_y < self.ball_y < self.left_paddle_y + 100) or \
           (self.ball_x >= 1840 and self.right_paddle_y < self.ball_y < self.right_paddle_y + 100):
            self.ball_dx *= -1
        
        # Если мяч выходит за границы
        if self.ball_x < 50:
            self.right_score += 1  # Правый игрок забивает
            self.reset_ball()
        elif self.ball_x > 1841:
            self.left_score += 1  # Левый игрок забивает
            self.reset_ball()

        # Проверка условий для записи времени
        self.check_and_update_record()

        self.update()

    def reset_ball(self):
        self.ball_x, self.ball_y = 900, 300
        self.ball_dx *= random.choice((-1, 1))
        self.ball_dy *= random.choice((-1, 1))

    def update_time(self):
        self.elapsed_time += 1
        self.update()

    def check_and_update_record(self):
        if self.left_score == 10:
            self.update_record("left", self.elapsed_time)
        elif self.right_score == 10:
            self.update_record("right", self.elapsed_time)

    def update_record(self, player, new_time):
        try:
            with open("D:\\игра\\records.txt", "r") as file:
                lines = file.readlines()

            if player == "left":
                record_line_index = 1  # Вторая строка для левого игрока
            else:
                record_line_index = 2  # Третья строка для правого игрока

            current_record = int(lines[record_line_index].strip())

            if new_time < current_record:
                lines[record_line_index] = f"{new_time}\n"
                with open("D:\\игра\\records.txt", "w") as file:
                    file.writelines(lines)

        except Exception as e:
            print(f"Ошибка при обновлении записей: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пинг-Понг")
        self.setCentralWidget(PingPongGame())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
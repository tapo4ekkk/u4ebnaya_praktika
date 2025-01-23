import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QSlider, QDialog, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QPainter, QKeyEvent, QPen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class PingPongGame(QWidget):
    def __init__(self, ball_speed=10, paddle_length=100, exit_to_menu_callback=None):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setGeometry(100, 100, 800, 600)

        self.ball_speed = ball_speed
        self.paddle_length = paddle_length
        self.exit_to_menu_callback = exit_to_menu_callback

        # Инициализация мяча и ракеток
        self.ball_x = 900
        self.ball_y = 300
        self.ball_dx = self.ball_speed * random.choice((1, -1))
        self.ball_dy = self.ball_speed * random.choice((1, -1))

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

        self.back_to_menu_button = QPushButton("В меню", self)
        self.back_to_menu_button.setGeometry(60, 10, 100, 30)
        self.back_to_menu_button.clicked.connect(self.exit_to_menu)
        
        # Инициализация и воспроизведение музыки
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("D:\\игра\\Тетрис - Тетрис.mp3")))
        self.player.setVolume(50)  # Уровень громкости (0-100)
        self.player.play()  # Начать воспроизведение

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(Qt.white)

        # Ракетки
        painter.drawRect(50, self.left_paddle_y, 10, self.paddle_length)  # Левый
        painter.drawRect(1850, self.right_paddle_y, 10, self.paddle_length)  # Правый

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
        elif event.key() == Qt.Key_S and self.left_paddle_y < 990 - self.paddle_length:
            self.left_paddle_y += 20
        elif event.key() == Qt.Key_Up and self.right_paddle_y > 10:
            self.right_paddle_y -= 20
        elif event.key() == Qt.Key_Down and self.right_paddle_y < 990 - self.paddle_length:
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
        if (self.ball_x <= 60 and self.left_paddle_y < self.ball_y < self.left_paddle_y + self.paddle_length) or \
           (self.ball_x >= 1840 and self.right_paddle_y < self.ball_y < self.right_paddle_y + self.paddle_length):
            self.ball_dx *= -1
        
        # Если мяч выходит за границы
        if self.ball_x < 50:
            self.right_score += 1
            self.reset_ball()
        elif self.ball_x > 1841:
            self.left_score += 1
            self.reset_ball()

        self.update()

    def reset_ball(self):
        self.ball_x, self.ball_y = 900, 300
        self.ball_dx = self.ball_speed * random.choice((-1, 1))
        self.ball_dy = self.ball_speed * random.choice((-1, 1))

    def update_time(self):
        self.elapsed_time += 1
        self.update()

    def exit_to_menu(self):
        if self.exit_to_menu_callback:
            self.exit_to_menu_callback()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.ball_speed_slider = QSlider(Qt.Horizontal)
        self.ball_speed_slider.setMinimum(5)
        self.ball_speed_slider.setMaximum(30)
        self.ball_speed_slider.setValue(10)
        layout.addWidget(QLabel("Скорость мяча"))
        layout.addWidget(self.ball_speed_slider)

        self.paddle_length_slider = QSlider(Qt.Horizontal)
        self.paddle_length_slider.setMinimum(50)
        self.paddle_length_slider.setMaximum(200)
        self.paddle_length_slider.setValue(100)
        layout.addWidget(QLabel("Длина ракеток"))
        layout.addWidget(self.paddle_length_slider)

        self.confirm_button = QPushButton("Сохранить")
        self.confirm_button.clicked.connect(self.accept)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def get_settings(self):
        return self.ball_speed_slider.value(), self.paddle_length_slider.value()

class LeaderboardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Таблица лидеров")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.leaderboard_text = QTextEdit()
        self.leaderboard_text.setReadOnly(True)
        layout.addWidget(self.leaderboard_text)

        self.load_leaderboard()
        self.setLayout(layout)

    def load_leaderboard(self):
        try:
            with open("D:\\игра\\records.txt", "r") as file:
                self.leaderboard_text.setText(file.read())
        except FileNotFoundError:
            self.leaderboard_text.setText("Файл с рекордами не найден.")
        except Exception as e:
            self.leaderboard_text.setText(f"Ошибка загрузки таблицы лидеров: {e}")

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Меню игры")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        self.play_button = QPushButton("Играть")
        self.play_button.clicked.connect(self.start_game)
        layout.addWidget(self.play_button)

        self.settings_button = QPushButton("Настройки")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.rules_button = QPushButton("Правила")
        self.rules_button.clicked.connect(self.show_rules)
        layout.addWidget(self.rules_button)

        self.leaderboard_button = QPushButton("Таблица лидеров")
        self.leaderboard_button.clicked.connect(self.show_leaderboard)
        layout.addWidget(self.leaderboard_button)

        self.exit_button = QPushButton("Выход")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

        self.ball_speed = 10
        self.paddle_length = 100

    def start_game(self):
        self.game_window = QMainWindow()
        self.game_widget = PingPongGame(self.ball_speed, self.paddle_length, self.return_to_menu)
        self.game_window.setCentralWidget(self.game_widget)
        self.game_window.setWindowTitle("Пинг-Понг")
        self.game_window.show()
        self.close()

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            self.ball_speed, self.paddle_length = settings_dialog.get_settings()

    def show_rules(self):
        QMessageBox.information(self, "Правила", "Перемещайте ракетки, чтобы отбивать мяч. Счет бесконечный.")

    def show_leaderboard(self):
        leaderboard_dialog = LeaderboardDialog(self)
        leaderboard_dialog.exec_()

    def return_to_menu(self):
        self.game_window.close()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())

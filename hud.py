import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from activity import ActivitySignal
from tray import TrayIcon
from menu.settings import SettingsMenu
import threading


# [동물 카드]
class AnimalCard(QWidget):
    request_status = pyqtSignal(str)

    def __init__(self, user_id, nickname, animal):
        super().__init__()
        self.user_id = user_id
        self.nickname = nickname
        self.animal = animal
        self.init_ui()

    def init_ui(self):
        # 세로 레이아웃 (동물 이미지 위, 닉네임 아래)
        self.main_layout = QVBoxLayout()
        
        # 이미지 표시할 라벨 생성
        self.img_label = QLabel()
        # self.img_label.setFixedSize(100, 125)

        # 닉네임 표시할 라벨 생성
        self.nickname_label = QLabel(self.nickname)
        self.nickname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nickname_label.adjustSize()
        self.nickname_label.setStyleSheet("color: white;")

        self.main_layout.addWidget(self.img_label)
        self.main_layout.addWidget(self.nickname_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.main_layout)

        # 초기 이미지 설정 (closed 상태)
        self.set_status("closed")

    # 상태에 따라 이미지 전환하는 함수
    def set_status(self, status):
        base_path = f"assets/animals/{self.animal}"
        img_w = 80
        img_h = 100

        if status == "closed":
            # PNG 표시
            pixmap = QPixmap(f"{base_path}/close.png")
            pixmap = pixmap.scaled(img_w, img_h, Qt.AspectRatioMode.KeepAspectRatio)
            self.img_label.setPixmap(pixmap)

        elif status == "opening":
            movie = QMovie(f"{base_path}/open.gif")
            movie.setScaledSize(QSize(img_w, img_h))
            movie.finished.connect(lambda: self.request_status.emit("working"))
            self.img_label.setMovie(movie)
            self.movie = movie
            movie.start()

        elif status == "working":
            movie = QMovie(f"{base_path}/ing.gif")
            movie.setScaledSize(QSize(img_w, img_h))
            self.img_label.setMovie(movie)
            self.movie = movie
            movie.start()

        elif status == "closing":
            movie = QMovie(f"{base_path}/close.gif")
            movie.setScaledSize(QSize(img_w, img_h))
            movie.finished.connect(lambda: self.request_status.emit("closed"))
            self.img_label.setMovie(movie)
            self.movie = movie
            movie.start()



# [메인 창]
class HUDWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.start_activity()
        self.tray = TrayIcon(self)
        self.tray.setup()
        self.settings_menu = SettingsMenu(self)

    def init_ui(self):
        self.setWindowTitle("StudyPals")
        self.show()

        # 테두리 없애기
        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint |   # 테두리 제거
            Qt.WindowType.WindowStaysOnTopHint |   # 항상 최상단 유지
            Qt.WindowType.Tool   # 작업표시줄에 표시 안되는 툴창 형태
        ) 
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)   # 창 배경 투명 설정

        # 우측 하단 위치
        screen = QApplication.primaryScreen().geometry()  # 모니터 크기
        self.resize(100, 130)
        self.move(
            screen.width() - self.width() - 10,    # 오른쪽에서 20px
            screen.height() - self.height() - 65   # 아래에서 60px
        )

        # 레이아웃 설정 (카드들을 가로로 나열)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.my_card = AnimalCard(
            user_id=self.user_data["user_id"],
            nickname=self.user_data["nickname"],
            animal=self.user_data["animal"]
        )

        self.main_layout.addWidget(self.my_card)
        self.setLayout(self.main_layout)
        self.show()

    
    def start_activity(self):
        # ActivitySignal 인스턴스 생성
        self.monitor = ActivitySignal(user_id=self.user_data["user_id"])

        # Signal 과 my_card.set_status 연결
        # status_changed 시그널이 발생하면 self.my_card.set_status 함수를 실행하라
        self.monitor.status_changed.connect(self.my_card.set_status)
        # request_status 시그널이 발생하면 self.monitor.set_working 함수를 실행하라
        self.my_card.request_status.connect(self.monitor.on_card_finished)

        # 별도 스레드로 모니터링 시작
        threading.Thread(target=self.monitor.start_monitoring, daemon=True).start()


    # ------ 드래그 이동 ------
    # 마우스 클릭 시작점 저장
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    # 드래그로 창 이동
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()

    # ------ 우클릭 ------
    def contextMenuEvent(self, event):
        self.settings_menu.show(event.globalPos())

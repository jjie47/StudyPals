import sys
from datetime import datetime, timezone, timedelta
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
from activity import ActivitySignal
from tray import TrayIcon
from menu.settings import SettingsMenu
from group import get_my_groups
from firebase import get_db
import threading


def _is_offline(friend_data):
    if not friend_data.get("is_online", False):
        return True
    last_seen = friend_data.get("last_seen")
    if last_seen is None:
        return True
    return (datetime.now(timezone.utc) - last_seen) > timedelta(minutes=10)


# [동물 카드]
class AnimalCard(QWidget):
    request_status = pyqtSignal(str)

    def __init__(self, user_id, nickname, animal, size=(80, 100)):
        super().__init__()
        self.user_id = user_id
        self.nickname = nickname
        self.animal = animal
        self.card_size = size
        self.current_status = "closed"
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
        self.nickname_label.setFixedHeight(self.nickname_label.fontMetrics().height())
        self.nickname_label.setStyleSheet("color: #fff;")

        self.main_layout.addWidget(self.img_label)
        self.main_layout.addWidget(self.nickname_label)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setLayout(self.main_layout)

        # 초기 이미지 설정 (closed 상태)
        self.set_status("closed")

    # 상태에 따라 이미지 전환하는 함수
    def set_status(self, status):
        self.current_status = status
        base_path = f"assets/animals/{self.animal}"
        img_w, img_h = self.card_size
        self.setFixedWidth(img_w)
        self.img_label.setFixedSize(img_w, img_h)

        if status == "closed":
            # PNG 표시
            pixmap = QPixmap(f"{base_path}/close.png")
            pixmap = pixmap.scaled(
                img_w, img_h, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
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



class FriendStatusUpdater(QObject):
    status_changed = pyqtSignal(str)
    go_offline = pyqtSignal()

    def __init__(self, card):
        super().__init__()
        self.status_changed.connect(card.set_status)



# [메인 창]
class HUDWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.card_size = (80, 100)
        self.init_ui()
        self.start_activity()
        self.load_friend_cards()
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
            screen.width() - self.width() - 10,    # 오른쪽에서 10px
            screen.height() - self.height() - 85   # 아래에서 85px
        )

        # 레이아웃 설정 (카드들을 가로로 나열)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.my_card = AnimalCard(
            user_id=self.user_data["user_id"],
            nickname=self.user_data["nickname"],
            animal=self.user_data["animal"],
            size=self.card_size
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


    # ------ 그룹원 목록 가져오기 ------
    def load_friend_cards(self):
        db = get_db()
        groups = get_my_groups(self.user_data["user_id"])

        # 그룹원 user_id 목록 수집 (중복 제거)
        friend_ids = set()
        for group in groups:
            for member_id in group["members"]:
                if member_id != self.user_data["user_id"]:  # 나 제외
                    friend_ids.add(member_id)

        # 온라인 친구 카드만 추가
        online_ids = set()
        for friend_id in friend_ids:
            friend_data = db.collection("users").document(friend_id).get().to_dict()
            if _is_offline(friend_data):
                continue
            online_ids.add(friend_id)
            card = AnimalCard(
                user_id=friend_id,
                nickname=friend_data["nickname"],
                animal=friend_data["animal"],
                size=self.card_size
            )
            self.main_layout.addWidget(card)

            # 실시간 리스너 등록
            self.add_listener(friend_id, card)

        # 창 크기 자동 조절
        card_count = len(online_ids) + 1
        card_w, card_h = self.card_size
        new_width = card_w * card_count

        nickname_h = self.my_card.nickname_label.fontMetrics().height()
        new_height = card_h + nickname_h
        self.setMinimumSize(0, 0)
        self.setMaximumSize(new_width, new_height)
        self.resize(new_width, new_height)

        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() - self.width() - 20,
            screen.height() - self.height() - 85
        )


    def refresh_friend_cards(self):
        # 기존 친구 카드 제거 (내 카드 제외)
        while self.main_layout.count() > 1:
            item = self.main_layout.takeAt(1)
            if item.widget():
                item.widget().setParent(None)   # deleteLater() 대신 즉시 삭제!

        # 친구 카드 다시 불러오기
        self.load_friend_cards()


    def remove_friend_card(self, card):
        self.main_layout.removeWidget(card)
        card.setParent(None)
        count = self.main_layout.count()
        card_w = self.card_size[0]
        new_width = card_w * count
        nickname_h = self.my_card.nickname_label.fontMetrics().height()
        self.setMaximumSize(new_width, self.card_size[1] + nickname_h)
        self.resize(new_width, self.height())
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() - self.width() - 20,
            screen.height() - self.height() - 85
        )

    def apply_card_size(self, size):
        self.card_size = size
        card_w, card_h = size

        self.my_card.card_size = size
        self.my_card.set_status(self.monitor.current_status)

        for i in range(1, self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                card.card_size = size
                card.set_status(card.current_status)

        self.layout().activate()

        count = self.main_layout.count()
        new_width = card_w * count
        nickname_h = self.my_card.nickname_label.fontMetrics().height()
        new_height = card_h + nickname_h
        self.setMinimumSize(0, 0)
        self.setMaximumSize(new_width, new_height)
        self.resize(new_width, new_height)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() - self.width() - 20,
            screen.height() - self.height() - 85
        )

    def add_listener(self, user_id, card):
        updater = FriendStatusUpdater(card)
        self.updaters = getattr(self, 'updaters', [])
        self.updaters.append(updater)  # 가비지 컬렉션 방지
        updater.go_offline.connect(lambda: self.remove_friend_card(card))

        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                data = doc.to_dict()
                if _is_offline(data):
                    updater.go_offline.emit()
                    return
                updater.status_changed.emit(data.get("status", "closed"))

        db = get_db()
        db.collection("users").document(user_id).on_snapshot(on_snapshot)



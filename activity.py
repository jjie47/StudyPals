from pynput import keyboard, mouse
from firebase import get_db
from PyQt6.QtCore import QObject, pyqtSignal
import threading


# 사용자의 활동을 감지하고 상태를 관리
class ActivitySignal(QObject):
    db = get_db()

    # Firebase에 상태 업데이트
    def update_status(self, status):
        self.db.collection("users").document(self.user_id).update({
            "status": status
        })


    # 상태가 바뀔때 문자열을 담아서 Signal 발송
    status_changed = pyqtSignal(str)

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.current_status = "closed"      # 인스턴스 변수
        self.timer = None                   # 인스턴스 변수

    # 움직임 감지시 호출되는 함수
    def on_activity(self):
        # closed 상태면 -> opening 으로 변경
        if self.current_status == "closed":
            self.current_status = "opening"
            self.update_status("opening")
            self.status_changed.emit("opening")

        # opening 상태면 -> 무시
        elif self.current_status == "opening":
            pass

        # working 상태면 -> 타이머만 리셋
        elif self.current_status == "working":
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(10, self.set_closing)
            self.timer.start()

        # closing 상태면 -> working으로 복귀
        elif self.current_status == "closing":
            self.current_status = "working"
            self.update_status("working")
            self.status_changed.emit("working")

    def on_card_finished(self, status):
        if status == "working":
            self.set_working()
        elif status == "closed":
            self.set_closed()


    # working 으로 변경
    def set_working(self):
        self.current_status = "working"
        self.update_status("working")
        self.status_changed.emit("working")
    
    # closing 으로 변경
    def set_closing(self):
        self.current_status = "closing"
        self.update_status("closing")
        self.status_changed.emit("closing")

    # closed 로 변경
    def set_closed(self):
        self.current_status = "closed"
        self.update_status("closed")
        self.status_changed.emit("closed")



    # 키보드/마우스 이벤트 감지 시작
    def start_monitoring(self):
        self.update_status("closed")

        # 키보드 감지
        self.listener_kb = keyboard.Listener(on_press=lambda key: self.on_activity())
        # 마우스 감지
        self.listener_ms = mouse.Listener(
            on_move=lambda x, y: self.on_activity(), 
            on_click=lambda x, y, button, pressed: self.on_activity(), 
            on_scroll=lambda x, y, dx, dy: self.on_activity()
        )

        # 프로그램 종료 시 자동 종료되도록 daemon 설정
        self.listener_kb.daemon = True
        self.listener_ms.daemon = True

        # 감지 시작
        self.listener_kb.start()
        self.listener_ms.start()
        self.listener_kb.join()

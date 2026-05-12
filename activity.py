''' 키보드/마우스 움직임을 감지해서 Firebase에 상태를 업데이트 '''

# 구현할 것
#     1. 키보드/마우스 이벤트 감지
#     2. 움직임 감지되면 -> status : "active"로 Firebase 업데이트
#     3. 마지막 입력으로부터 10초 경과시 -> status : "inactive"로 Firebase 업데이트

from pynput import keyboard, mouse
from firebase import get_db
import threading


db = get_db()

# Firebase에 상태 업데이트
def update_status(user_id, status):
    db.collection("users").document(user_id).update({
        "status": status
    })


current_status = "closed"   # 현재 상태 전역변수
timer = None   # 타이머 전역변수

# 움직임 감지시 호출되는 함수
def on_activity(user_id):
    global timer, current_status

    # closed 상태면 -> opening 으로 변경
    if current_status == "closed":
        current_status = "opening"
        update_status(user_id, "opening")

        # open.gif 재생시간 만큼 후에 working으로 전환 (임시)
        timer = threading.Timer(1, lambda: set_working(user_id))
        timer.start()

    # opening 상태면 -> 무시
    elif current_status == "opening":
        pass

    # working 상태면 -> 타이머만 리셋
    elif current_status == "working":
        if timer:
            timer.cancel()
        timer = threading.Timer(10, set_closing, args=[user_id])
        timer.start()

    # closing 상태면 -> working으로 복귀
    elif current_status == "closing":
        current_status = "working"
        update_status(user_id, "working")


def set_working(user_id):
            global current_status
            current_status = "working"
            update_status(user_id, "working")
            
def set_closing(user_id):
    global current_status
    current_status = "closing"      # current_status 도 변경!
    update_status(user_id, "closing")

    # close.gif 재생시간 만큼 후에 closed로 전환 (임시)
    timer = threading.Timer(1, set_closed, args=[user_id])
    timer.start()

def set_closed(user_id):
    global current_status
    current_status = "closed"
    update_status(user_id, "closed")



# 키보드/마우스 이벤트 감지 시작
def start_monitoring(user_id):
    update_status(user_id, "closed")

    # 키보드 감지
    listener_kb = keyboard.Listener(on_press=lambda key: on_activity(user_id))
    # 마우스 감지
    listener_ms = mouse.Listener(
        on_move=lambda x, y: on_activity(user_id), 
        on_click=lambda x, y, button, pressed: on_activity(user_id), 
        on_scroll=lambda x, y, dx, dy: on_activity(user_id)
    )

    # 프로그램 종료 시 자동 종료되도록 daemon 설정
    listener_kb.daemon = True
    listener_ms.daemon = True

    # 감지 시작
    listener_kb.start()
    listener_ms.start()
    listener_kb.join()

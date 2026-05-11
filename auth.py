from firebase import get_db
import bcrypt

db = get_db()

# 회원가입
def signup(user_id: str, user_pw: str, nickname: str):
    # ID 정보 가져오기
    db_user = db.collection("users").document(user_id).get()

    # ID가 있으면
    if db_user.exists:   # 문서가 실제로 있을 때만 True
        raise ValueError("이미 존재하는 아이디입니다.")
    
    # 비밀번호 암호화
    hashed = bcrypt.hashpw(user_pw.encode(), bcrypt.gensalt())
    
    try:
        # DB 저장
        db.collection("users").document(user_id).set({
            "user_id": user_id,
            "user_pw": hashed,
            "nickname": nickname,
            "animal": "cat",
            "status": "inactive"
        })
        print("회원가입 성공!")
    except Exception as e:
        print(f"DB 저장 중 오류 발생 : {e}")


# 로그인
def login(user_id: str, user_pw: str) -> dict:
    # ID 확인
    db_user = db.collection("users").document(user_id).get()

    if not db_user.exists: 
        raise ValueError("존재하지 않는 아이디입니다.") 
    
    user_data = db_user.to_dict()   # 문서 내용을 딕셔너리로 변환
    
    # PW 확인
    check_pw = bcrypt.checkpw(user_pw.encode(), user_data["user_pw"])
    if not check_pw:
        raise ValueError("비밀번호가 일치하지 않습니다.")
    
    return {
        "nickname": user_data["nickname"],
        "animal": user_data["animal"]
    }

''' 회원가입, 로그인, 토큰생성, 자동로그인 '''

from firebase import get_db
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime
import json


# ------ 토큰 ------
# .env파일을 환경변수에 등록
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# [토큰 생성]
def create_token(data: dict):
    to_encode = data.copy()

    # 만료시간 설정
    expire = datetime.datetime.now() + datetime.timedelta(days=7)   # 7일 후 만료
    to_encode.update({"exp": expire})   # 만료시간 항목 추가

    # 데이터를 비밀키로 서명하여 JWT 문자열 생성
    # jwt.encode(payload, key, algorithm=...)
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # config.json 에 저장
    with open("secrets/config.json", "w") as f:
        json.dump({"token": token}, f)

    return token


# [토큰 검사]
def verify_token(token: str):
    try:
        # 토큰 복호화
        # jwt.decode(payload, key, algorithm=...)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 토큰 안에서 user_id 꺼내기
        user_id = payload.get("sub")

        return user_id
    
    except jwt.ExpiredSignatureError:
        # 로그인 창으로
        raise ValueError("토큰이 만료되었습니다.")

    except jwt.InvalidTokenError:
        # 로그인 창으로
        raise ValueError("유효하지 않은 토큰")



# ------ 메인로직 ------
db = get_db()

# [회원가입]
def signup(user_id: str, user_pw: str, nickname: str, animal: str):
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
            "animal": animal,
            "status": "closed"
        })
        print("회원가입 성공!")
    except Exception as e:
        print(f"DB 저장 중 오류 발생 : {e}")


# [로그인]
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
    
    # 토큰 생성
    access_token = create_token(data= {"sub": user_data["user_id"]})

    return {
        "user_id": user_data["user_id"],
        "nickname": user_data["nickname"],
        "animal": user_data["animal"],
        "access_token": access_token
    }


# [자동로그인]
def auto_login():
    # config.json 파일 읽기
    with open("secrets/config.json", "r") as f:
        config = json.load(f)
        token = config["token"]

    user_id = verify_token(token)
    
    # 유저 정보 가져오기
    db_user = db.collection("users").document(user_id).get()
    user_data = db_user.to_dict()   # 문서 내용을 딕셔너리로 변환

    return {
        "user_id": user_data["user_id"],
        "nickname": user_data["nickname"],
        "animal": user_data["animal"],
    }
import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (X 수익화 최적화 및 기억력 고정)
SYSTEM_PROMPT = """
당신은 X(트위터)에서 가장 핫한 '지식 브런치' 작가입니다. 
당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'입니다.

[절대 규칙: 번호 인식 및 중복 방지]
1. 사용자가 번호(예: 7번, 7번 써줘)를 말하면, 반드시 '직전 대화에서 당신이 제시한 리스트'의 해당 번호 제목을 주제로 잡으세요. 
2. 숫자 그 자체(예: 숫자 7의 의미)에 대해 쓰는 것은 절대 금지입니다. 
3. 당신이 한 번이라도 본문을 작성한 주제는 기억해 두었다가 다음 리스트 제안 시 반드시 제외하세요.

[무조건 지켜야 할 출력 양식]
1. 제목: 무조건 임팩트 있는 한 줄. (## 금지, 특수문자 금지)
2. 여백: 제목 바로 뒤에 반드시 '엔터 두 번' (빈 줄 2개) 무조건 삽입.
3. 본문 개행: 한 문장이 15~20자 사이면 무조건 엔터 (모바일 최적화).
4. 본문 간격: 문장과 문장 사이는 무조건 한 줄 띄우기.
5. 말투: 설명충 말투 금지. 자극적이고 유머러스한 팩트 중심.

[본문 예시]
왜 자다가 낭떠러지에서 떨어질까요?


평온하게 잠들려던 순간 
몸이 움찔하며 깨셨나요?

우리 뇌가 당신의 목숨을 
구하려고 벌이는 착각입니다

심박수가 급격히 떨어지면 
뇌는 당신이 죽는 줄 알고 

살리려고 강력한 전기 신호를 
순식간에 쏴버리는 겁니다
"""

# 3. 모델 및 채팅 세션 초기화 (함수 밖에서 실행하여 대화 맥락 영구 유지)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)
# 이 chat_session이 파트너님이 받은 10개 리스트를 끝까지 기억합니다.
chat_session = model.start_chat(history=[])

async def handle_message(update: Update, context: Context

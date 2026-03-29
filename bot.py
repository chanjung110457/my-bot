import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (X 수익화 최적화 + 제목 고정 로직)
SYSTEM_PROMPT = """
당신은 X(트위터)에서 조회수 수백만을 찍는 '지식 큐레이터'입니다. 
당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'입니다.

[리스트 작성 철칙 - 적재적소 어그로]
1. 제목 스타일: 무조건 질문형일 필요는 없습니다. 주제에 따라 가장 '맛깔나고 궁금한' 형식을 취하세요.
   - 질문형 예시: "기시감 느껴본 적 있으세요?", "가위 눌려보셨나요?"
   - 팩트 폭격형 예시: "문어의 다리가 많은 진짜 이유", "우주에서 소리 지르면 생기는 일"
   - 호기심 자극형 예시: "당신이 몰랐던 바퀴벌레의 비밀", "죽기 직전 뇌에서 일어나는 일"

2. 장르 믹스: 아래 카테고리를 골고루 섞어 10개를 뽑으세요. (미스터리/공포, 우주/심해, 동물/인체, 일상/공감 등)

[본문 작성 철칙]
1. 제목 고정: 사용자가 번호를 말하면, 반드시 '직전 대화'의 리스트에 있는 해당 번호의 제목을 '토씨 하나' 틀리지 말고 그대로 제목으로 쓰세요. (임의 수정 절대 금지)
2. 양식: 제목 1줄 -> 빈 줄 2개 -> 20자 내외 개행 본문 (문장 사이 빈 줄 1개).
3. 말투: 설명충 금지. 자극적이고 유머러스한 팩트 중심. (인사말/서론 절대 금지)

[본문 예시 - 이 느낌 그대로 쓰세요]
왜 자다가 낭떠러지에서 떨어질까요?


평온하게 잠들려던 순간 
몸이 움찔하며 깨셨나요?

우리 뇌가 당신의 목숨을 
구하려고 벌이는 착각입니다

잠이 들면서 심박수가 
급격히 떨어지면

우리 뇌는 당신의 몸이 
죽어가고 있다고 오해합니다

그래서 당신을 살리려고 
강력한 전기 신호를 

순식간에 쏴버리는 겁니다
"""

# 사용자별 대화 세션을 저장할 딕셔너리 (기억력 핵심)
user_chats = {}

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
    return "gemini-1.5-flash"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
        
        # 파트너님별로 대화 흐름(기억)을 유지하도록 세션 연결
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[])
        
        chat = user_chats[user_id]
        
        # 파트너님의 입력을 받아서 처리 (기억 유지하며 전송)
        response = chat.send_message(
            update.message.text, 
            generation_config={"temperature": 0.8}
        )
        await update.message.reply_text(response.text)
        
    except Exception as e:
        # 에러 발생 시 해당 세션 초기화하여 봇이 멈추지 않게 방어
        if user_id in user_chats:
            del user_chats[user_id]
        await update.message.reply_text(f"에러 발생: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("파트너님, 제목 박제 및 기억력 모드 가동되었습니다!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

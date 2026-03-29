import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (궁금증 유발 제목 + 박제 로직)
SYSTEM_PROMPT = """
당신은 X(트위터)에서 가장 핫한 '지식 브런치' 작가입니다. 
당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'입니다.

[리스트 작성 철칙]
1. 주제 리스트를 뽑을 때, 제목은 반드시 "궁금해서 클릭할 수밖에 없는 질문형"으로 만드세요.
   (예: "데자뷰 겪어본 적 있으신가요?", "양파가 왜 나를 울게 만들까요?")

[본문 작성 철칙]
1. 제목 고정: 사용자가 번호(예: 1번)를 말하면, 반드시 직전 리스트에 있는 해당 번호의 제목을 토씨 하나 틀리지 말고 그대로 제목으로 쓰세요. 임의로 제목을 더 멋있게 고치지 마세요.
2. 제목 양식: 무조건 한 줄. (## 금지, 특수문자 금지)
3. 여백: 제목 쓰고 엔터 두 번(빈 줄 2개) 필수.
4. 본문 개행: 한 문장이 15~20자 사이면 무조건 엔터. (모바일 최적화)
5. 본문 간격: 문장과 문장 사이는 무조건 한 줄 띄우세요.
6. 말투: "데자뷔 현상은~" 같은 설명충 말투 쓰면 즉시 해고입니다. 
   (예시: "우리 뇌가 당신을 살리려고 댄스를 추는 셈입니다.")

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

# 사용자별 대화 세션 저장 (기억력 유지)
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
        
        # 세션이 없거나 초기화가 필요한 경우 대응
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[])
        
        chat = user_chats[user_id]
        
        # 파트너님의 입력을 받아서 처리
        response = chat.send_message(
            update.message.text, 
            generation_config={"temperature": 0.8}
        )
        await update.message.reply_text(response.text)
        
    except Exception as e:
        # 에러 발생 시 세션 리셋 (충돌 방지)
        if user_id in user_chats:
            del user_chats[user_id]
        print(f"Error detail: {e}")
        await update.message.reply_text("봇이 다시 가동 중입니다. 한 번 더 입력해주세요!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("파트너님, 제목 낚시력 강화 모드 가동 중!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

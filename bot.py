import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (기억력 + 본문 예시 + 번호 인식)
SYSTEM_PROMPT = """
당신은 X(트위터) '지식 브런치' 작가입니다. 당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'입니다.

[절대 규칙]
1. 번호 인식: 사용자가 번호(예: 7번)를 말하면, 반드시 이전 대화에서 당신이 준 리스트의 해당 제목을 주제로 본문을 작성하세요.
2. 본문 양식: 제목 한 줄 -> 빈 줄 2개 -> 20자 내외 개행 본문 (문장 사이 빈 줄 1개).
3. 말투: 설명충 금지. 자극적이고 유머러스한 팩트 중심. 인사말이나 사설 절대 금지.

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

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

# 서버가 재시작되어도 파트너님과의 대화를 기억하기 위한 세션 관리
sessions = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # 사용자별 대화 세션 유지 (기억력의 핵심)
        if user_id not in sessions:
            sessions[user_id] = model.start_chat(history=[])
        
        chat = sessions[user_id]
        response = chat.send_message(update.message.text, generation_config={"temperature": 0.8})
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("내용을 생성하지 못했습니다. 다시 시도해주세요!")
            
    except Exception as e:
        # 에러 발생 시 세션 초기화 후 재시도
        if user_id in sessions:
            del sessions[user_id]
        print(f"Error: {e}")
        await update.message.reply_text("봇이 다시 가동 중입니다. 한 번 더 입력해주세요!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("파트너님, 기억력 복구 완료! Railway 배포 확인하세요.")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

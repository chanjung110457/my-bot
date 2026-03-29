import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (본문 예시 + 번호 인식 + 철저한 양식)
SYSTEM_PROMPT = """
당신은 X(트위터) '지식 브런치' 채널의 전문 작가입니다. 
당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'처럼 행동하세요.

[본문 예시 - 무조건 이 말투와 양식을 복제하세요]
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

[지식 브런치 철칙]
1. 번호 인식: 사용자가 번호(예: 7번)를 말하면, 해당 숫자가 포함된 주제를 유추해서 본문을 작성하세요. 숫자 자체에 대해 쓰는 것은 절대 금지입니다.
2. 양식: 제목 한 줄 -> 빈 줄 2개 -> 20자 내외 개행 본문 (문장 사이 빈 줄 1개).
3. 금지: ## 특수문자 금지, 인사말 금지, 설명충 말투 금지.
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        # 매번 독립적으로 생성하여 서버 부하 및 세션 꼬임 방지 (Railway 최적화)
        response = model.generate_content(
            update.message.text,
            generation_config={"temperature": 0.8}
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("잠시 오류가 있었습니다. 다시 보내주세요!")
            
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("봇이 다시 가동 중입니다. 한 번 더 입력해주세요!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("가동 시작...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

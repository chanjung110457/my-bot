import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 핵심 지침 (본문 예시와 철칙만 압축)
SYSTEM_PROMPT = """
당신은 X(트위터) 작가입니다. 인사말 없이 바로 본론만 씁니다.

[본문 예시 - 이 양식 그대로 복제]
왜 자다가 낭떠러지에서 떨어질까요?


평온하게 잠들려던 순간 
몸이 움찔하며 깨셨나요?

우리 뇌가 당신의 목숨을 
구하려고 벌이는 착각입니다

심박수가 급격히 떨어지면 
뇌는 당신이 죽는 줄 알고 

살리려고 강력한 전기 신호를 
순식간에 쏴버리는 겁니다

[철칙]
1. 번호 입력 시: 해당 번호의 주제로 위 예시처럼 본문 작성. 숫자 설명 금지.
2. 양식: 제목 1줄 -> 빈 줄 2개 -> 20자 내외 개행 본문 (문장 사이 빈 줄 1개).
3. 절대 금지: ##, "알겠습니다", "좋습니다" 같은 사설.
"""

model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        # 안전한 응답 생성을 위해 세이프티 세팅 해제 및 온도 조절
        response = model.generate_content(
            update.message.text,
            generation_config={"temperature": 0.8}
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("내용 생성에 실패했습니다. 다시 입력해주세요.")
            
    except Exception as e:
        # 에러 발생 시 로그만 찍고 재시도 유도
        print(f"Error: {e}")
        await update.message.reply_text("다시 한번 말씀해주세요!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

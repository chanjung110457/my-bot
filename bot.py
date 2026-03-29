import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 환경변수 읽기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))

# Gemini 설정 (최신 안정화 모델명으로 변경)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

SYSTEM_PROMPT = "당신은 X(트위터) 포스팅 전문가입니다. 주제 추천과 본문 작성을 도와주세요."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID: return 

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        # 간단한 텍스트 생성 방식 사용
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\n사용자 요청: {update.message.text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"에러: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

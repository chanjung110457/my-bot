import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Railway에서 설정한 변수 가져오기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Gemini 설정
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 메시지가 오면 무조건 대답 시도
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        # 에러가 나면 텔레그램으로 바로 보고
        await update.message.reply_text(f"에러 발생: {str(e)}")

def main():
    # 봇 시작
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("봇 가동 중...")
    app.run_polling()

if __name__ == '__main__':
    main()

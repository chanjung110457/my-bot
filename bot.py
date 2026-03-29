import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 환경변수 로드
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Gemini 설정
genai.configure(api_key=GOOGLE_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # 시도해볼 모델 목록 (에러 회피용)
    model_names = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    
    response_text = ""
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(update.message.text)
            response_text = response.text
            if response_text: break # 성공하면 중단
        except Exception:
            continue # 실패하면 다음 모델로 시도

    if response_text:
        await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("구글 API 응답 오류입니다. API 키가 활성화될 때까지 5분만 기다려주세요.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

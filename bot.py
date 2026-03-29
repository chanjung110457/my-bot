import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 로드
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# 2. Gemini 설정
genai.configure(api_key=GOOGLE_API_KEY)

def get_working_model():
    # 현재 키로 사용 가능한 모델 리스트를 가져와서 첫 번째 놈을 잡습니다.
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
    return "models/gemini-1.5-flash" # 최후의 수단

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        # 매번 모델을 새로 확인해서 에러를 피합니다.
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"에러 발생: {str(e)}\n사용 시도 모델: {model_name}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

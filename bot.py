import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 읽기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# 2. Gemini 설정 (가장 정확한 경로 지정)
genai.configure(api_key=GOOGLE_API_KEY)

# 404 에러를 방지하기 위해 'models/'를 명시적으로 붙입니다.
model = genai.GenerativeModel('models/gemini-1.5-flash')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 사용자가 메시지를 보내면 봇이 '입력 중...' 상태를 표시합니다.
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # 3. 구글 AI에게 요청 전송
        response = model.generate_content(update.message.text)
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("AI가 응답을 생성하지 못했습니다. 다시 시도해주세요.")
            
    except Exception as e:
        # 에러 발생 시 내용을 텔레그램으로 전송
        await update.message.reply_text(f"알림: 현재 연결 경로를 재설정 중입니다.\n내용: {str(e)}")

def main():
    # 봇 시작
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Gemini 봇 가동 시작!")
    app.run_polling()

if __name__ == '__main__':
    main()

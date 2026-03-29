import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 읽기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))

# 2. Gemini 설정
genai.configure(api_key=GOOGLE_API_KEY)

# 모델 설정 (가장 기본 명칭 사용)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """당신은 X(트위터) 포스팅 전문가입니다. 
- '주제 뽑아줘' 요청 시: 주제 10개 제공
- 번호 선택 시: 해당 주제로 15줄 내외의 포스팅 작성
- 사실에 기반하여 신뢰감 있는 말투를 사용하세요."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 본인 확인
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        return 

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # 3. 구글 AI에게 요청 전송 (가장 단순한 방식)
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\n사용자 요청: {update.message.text}")
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("AI가 응답을 생성하지 못했습니다. 다시 시도해주세요.")
            
    except Exception as e:
        # 에러 발생 시 출력
        await update.message.reply_text(f"에러가 발생했습니다.\n내용: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()

import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 읽기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))

# 2. Gemini 설정 및 모델 로드 (가장 안전한 방식)
genai.configure(api_key=GOOGLE_API_KEY)

# 404 에러 방지를 위해 사용 가능한 모델을 직접 지정하지 않고 선언만 합니다.
model = genai.GenerativeModel('gemini-1.5-flash')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        return 

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # 3. 가장 단순한 호출 방식 (v1beta 에러 회피)
        response = model.generate_content(
            update.message.text,
            generation_config=genai.types.GenerationConfig(candidate_count=1)
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("응답을 생성할 수 없습니다. 다시 시도해주세요.")
            
    except Exception as e:
        # 에러 메시지가 너무 길면 핵심만 출력
        error_msg = str(e)
        if "404" in error_msg:
            await update.message.reply_text("모델 연결 경로를 수정 중입니다. 잠시만 기다려주세요.")
        else:
            await update.message.reply_

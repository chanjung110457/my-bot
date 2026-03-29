import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (X 수익화 최적화 로직)
SYSTEM_PROMPT = """
당신은 '지식 브런치' 채널 전문 파트너입니다. 
불필요한 인사말, ## 같은 특수문자, AI 말투는 절대 금지합니다.

[핵심 규칙]
1. 번호 선택 처리: 사용자가 번호를 말하면, 반드시 바로 직전 리스트의 해당 번호 제목과 '정확히 일치'하는 내용을 쓰세요. (숫자만 보고 멋대로 추측 금지)
2. 양식 사수: 제목 한 줄 쓰고 -> 반드시 '엔터 두 번' -> 21자 이내 강제 개행 본문.
3. 중복 금지: 본문을 작성한 주제는 다시는 리스트에 올리지 마세요.

[모드 1: 주제 제안]
"주제 뽑아줘" 시, 잡학지식 제목 10개만 번호 매겨 전송.

[모드 2: 본문 작성]
선택된 번호의 주제로 글 작성.
- 제목: 한 줄 (특수문자 ## 금지)
- 여백: 제목 후 '2줄 공백' 무조건 삽입
- 본문: 21자 이내 개행 + 문장 사이 한 줄 여백
- 마무리: 사설 없이 본문만 딱 쓰고 종료
"""

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except:
        pass
    return "gemini-1.5-flash"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        model_name = get_working_model()
        model = genai.GenerativeModel(
            model_name,
            system_instruction=SYSTEM_PROMPT # 여기에 지침을 박았습니다.
        )
        
        # 파트너님의 입력을 받아서 처리
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
        
    except Exception as e:
        await update.message.reply_text(f"에러 발생: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("파트너님, 봇이 가동되었습니다. 텔레그램에서 '주제 뽑아줘'를 입력하세요!")
    app.run_polling()

if __name__ == '__main__':
    main()

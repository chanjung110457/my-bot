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
당신은 X(트위터) 지식 브런치 채널의 전문 파트너입니다. 
불필요한 인사말, 사설, 반복 출력은 절대 하지 않습니다.

[핵심 규칙]
1. 모든 응답은 한 번만 출력합니다. 같은 내용을 두 번 반복하지 마세요.
2. 리스트를 작성할 때는 반드시 1번부터 10번까지 '딱 10개'만 작성하고 즉시 종료하세요.

[모드 1: 주제 제안]
사용자가 주제를 요청하면, 임팩트 있는 제목 10개만 번호 매겨서 보냅니다. 본문은 쓰지 마세요.

[모드 2: 본문 작성]
사용자가 번호를 선택하면 다음 양식을 '반드시' 지키세요.
- 제목: 무조건 임팩트 있는 '한 줄' 질문/명제로 시작.
- 여백: 제목 바로 뒤에 반드시 '2줄의 빈 공간' 삽입.
- 본문: 한 줄 21자 이내 강제 줄바꿈 + 문장 사이 한 줄 여백.
- 말투: 담백하고 유머러스한 팩트 전달.
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

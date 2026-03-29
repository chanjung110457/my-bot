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
당신은 '여러가지 궁금해할만한 잡학지식' 채널을 운영하는 잡학사전 전문가입니다. 
당신의 역할은 사람들이 몰랐던 충격적이고 재미있는 '잡다한 지식'을 발굴하는 것입니다.

[핵심 규칙: 중복 금지]
1. 본문 작성 이력 관리: 당신이 한 번이라도 '본문'을 작성해준 주제는 당신의 데이터베이스에서 영구 제외합니다. 
2. 주제 제안 시, 이전에 본문으로 작성했던 내용은 절대로 다시 리스트에 포함하지 마세요.
3. "다른 주제로 가자"라고 하면, 기존에 나왔던 10개와는 완전히 다른 새로운 분야의 지식을 가져옵니다.

[작동 모드]
1. 주제 제안: "주제 뽑아줘" 시, 임팩트 있는 제목 10개만 번호 매겨서 전송. (딱 10개만 쓰고 종료)
2. 본문 작성: 번호 선택 시 아래 양식 엄수.
   - 제목: 임팩트 있는 '한 줄' 질문/명제
   - 여백: 제목 바로 뒤에 반드시 '2줄의 빈 공간' 삽입
   - 본문: 한 줄 21자 이내 강제 줄바꿈 + 문단 사이 한 줄 여백
   - 말투: 담백하고 유머러스한 정보 전달 (사설/인사 금지)
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

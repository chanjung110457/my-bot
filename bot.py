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
당신은 X(트위터)에서 가장 핫한 '지식 브런치' 작가입니다. 
당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'입니다.

[무조건 지켜야 할 철칙]
1. 제목: 무조건 한 줄. (## 금지, 특수문자 금지)
2. 여백: 제목 쓰고 엔터 두 번(빈 줄 2개) 무조건 넣으세요.
3. 본문 개행: 한 문장이 15~20자 사이면 무조건 엔터 치세요. (모바일 최적화)
4. 본문 간격: 문장과 문장 사이는 무조건 한 줄 띄우세요.
5. 말투: "데자뷔 현상은~" 같은 설명충 말투 쓰면 즉시 해고입니다. 
   (예시: "우리 뇌가 당신을 살리려고 댄스를 추는 셈입니다.")

[본문 예시 - 이 느낌 그대로 쓰세요]
왜 자다가 낭떠러지에서 떨어질까요?


평온하게 잠들려던 순간 
몸이 움찔하며 깨셨나요?

우리 뇌가 당신의 목숨을 
구하려고 벌이는 착각입니다

잠이 들면서 심박수가 
급격히 떨어지면

우리 뇌는 당신의 몸이 
죽어가고 있다고 오해합니다

그래서 당신을 살리려고 
강력한 전기 신호를 

순식간에 쏴버리는 겁니다

# SYSTEM_PROMPT 내 본문 작성 지침에 추가
"사용자가 번호를 말하면, 반드시 리스트에 있는 해당 번호의 '제목 내용'을 주제로 잡으세요. 숫자 자체에 대해 쓰지 마세요."

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
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT, generation_config={"temperature": 0.8})
        
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

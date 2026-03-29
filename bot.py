import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 1. 환경변수 및 Gemini 설정
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 파트너 전용 지침 (유연한 제목 + 장르 무제한 + 제목 고정)
SYSTEM_PROMPT = """
당신은 X(트위터)에서 조회수 수백만을 찍는 '지식 큐레이터'입니다. 
당신은 백과사전이 아닙니다. 사람을 홀리는 '글쟁이'입니다.

[리스트 작성 철칙 - 적재적소 어그로]
1. 제목 스타일: 무조건 질문형일 필요는 없습니다. 주제에 따라 가장 '맛깔나고 궁금한' 형식을 취하세요.
   - 질문형 예시: "기시감 느껴본 적 있으세요?", "가위 눌려보셨나요?"
   - 팩트 폭격형 예시: "문어의 다리가 많은 진짜 이유", "우주에서 소리 지르면 생기는 일"
   - 호기심 자극형 예시: "당신이 몰랐던 바퀴벌레의 비밀", "죽기 직전 뇌에서 일어나는 일"

2. 장르 믹스: 아래 카테고리를 골고루 섞어 10개를 뽑으세요. (미스터리/공포, 우주/심해, 동물/인체, 일상/공감 등)

[본문 작성 철칙]
1. 제목 고정: 사용자가 번호를 말하면, 반드시 '직전 대화'의 리스트에 있는 해당 번호의 제목을 '토씨 하나' 틀리지 말고 그대로 제목으로 쓰세요. (임의 수정 절대 금지)
2. 양식: 제목 1줄 -> 빈 줄 2개 -> 20자 내외 개행 본문 (문장 사이 빈 줄 1개).
3. 말투: 설명충 금지. 자극적이고 유머러스한 팩트 중심. (인사말/서론 절대 금지)
"""

# 사용자별 대화 세션을 담을 메모리 (Railway 재시작 전까지 유지)
user_chats = {}

def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
    except: pass
    return "gemini-1.5-flash"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not update.message or not update.message.text: return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
        
        # 세션이 없으면 새로 생성, 있으면 기존 세션(기억) 사용
        if user_id not in user_chats:
            user_chats[user_id] = model.start_chat(history=[])
        
        chat = user_chats[user_id]
        
        # 파트너님의 입력을 모델에게 전달 (이전 리스트 내용을 기억한 상태로 답변)
        response = chat.send_message(
            update.message.text, 
            generation_config={"temperature": 0.8}
        )
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("봇이 답변을 생성하지 못했습니다. 다시 시도해 주세요.")
            
    except Exception as e:
        # 오류 발생 시 세션 리셋 후 로그 출력
        print(f"Error for user {user_id}: {e}")
        if user_id in user_chats:
            del user_chats[user_id]
        await update.message.reply_text("봇이 다시 가동 중입니다. 한 번 더 입력해주세요!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    # 텍스트 메시지 처리 핸들러
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("파트너님, 기억력 보강 완료! 적재적소 낚시 모드 가동 중!")
    # 이전 밀린 메시지 무시하고 실행
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

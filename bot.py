import os
import anthropic
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "0"))

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """당신은 X(트위터) 포스팅 콘텐츠를 만들어주는 어시스턴트입니다.

주요 역할:
1. 사용자가 "주제 뽑아줘" 또는 비슷한 요청을 하면 → 주제 10개를 번호와 함께 제공
2. 사용자가 번호를 선택하면 (예: "1,3,5번으로 글 써줘") → 해당 주제로 완성본 포스팅 작성
3. 수정 요청이 있으면 → 즉시 수정해서 제공

주제 선정 기준:
- 일상에서 한번쯤 궁금했을 법한 것
- 과학, 심리, 자연, 신체, 사회 등 다양하게
- 제목만 봐도 클릭하고 싶어지는 것
- 너무 뻔하거나 이미 많이 알려진 것 제외

포스팅 작성 기준:
- 존댓말 사용 (습니다/입니다 체)
- 개인 의견 없이 사실만 전달
- 과학적/사실적 근거로 완벽하게 설명
- 해결방법이 있는 주제면 마지막에 해결방법 추가, 없으면 생략
- 길이 15줄 내외
- 복붙해서 바로 올릴 수 있게 완성본으로
- 제목은 첫 줄에, 읽고 싶어지게

포스팅 형식:
[제목 - 호기심을 자극하는 질문형]

[현상/사실 설명 - 과학적 근거로 상세하게]

[해결방법 - 해당되는 경우만]

대화는 항상 존댓말로 친절하게 합니다."""

conversation_history = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("접근 권한이 없습니다.")
        return
    
    user_message = update.message.text
    
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # 대화 기록이 너무 길어지면 앞부분 자름 (최근 20개만 유지)
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=conversation_history[user_id]
    )
    
    assistant_message = response.content[0].text
    
    conversation_history[user_id].append({
        "role": "assistant",
        "content": assistant_message
    })
    
    # 메시지가 너무 길면 분할 전송
    if len(assistant_message) > 4000:
        chunks = [assistant_message[i:i+4000] for i in range(0, len(assistant_message), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(assistant_message)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("봇 시작됨!")
    app.run_polling()

if __name__ == "__main__":
    main()

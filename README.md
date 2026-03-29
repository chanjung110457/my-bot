# X 포스팅 텔레그램 봇 배포 가이드

## 파일 구성
- bot.py - 메인 봇 코드
- requirements.txt - 필요한 패키지
- Procfile - Railway 실행 설정

## Railway 배포 순서

### 1. GitHub 업로드
1. github.com 가입
2. 새 레포지토리 생성 (이름 아무거나)
3. 파일 3개 업로드 (bot.py, requirements.txt, Procfile)

### 2. Railway 배포
1. railway.app 접속 → GitHub으로 로그인
2. "New Project" → "Deploy from GitHub repo"
3. 방금 만든 레포지토리 선택

### 3. 환경변수 설정 (중요!)
Railway 프로젝트 → Variables 탭에서 아래 3개 추가:

| 변수명 | 값 |
|--------|-----|
| TELEGRAM_TOKEN | 텔레그램 봇 토큰 |
| ANTHROPIC_API_KEY | Claude API 키 |
| ALLOWED_USER_ID | 본인 텔레그램 ID |

### 4. 본인 텔레그램 ID 확인 방법
텔레그램에서 @userinfobot 검색 → /start 입력 → ID 숫자 확인

### 5. 배포 완료
Variables 저장하면 자동으로 재시작됨
텔레그램 봇에 메시지 보내서 테스트!

## 사용법
- "오늘 주제 뽑아줘" → 주제 10개 받기
- "1,3,5번으로 글 써줘" → 완성본 포스팅 받기
- "3번 제목 더 자극적으로 바꿔줘" → 수정 요청
- 그냥 자연스럽게 대화하면 됨!

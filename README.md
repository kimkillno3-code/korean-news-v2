# 한국 정치 뉴스 클리핑 자동화

매일 오전 9시에 한국 주요 언론사의 정치 뉴스를 수집해서 이메일로 전송하는 시스템입니다.

## 🚀 설치 및 설정

### 1. GitHub 저장소 생성
1. GitHub에서 새 저장소 생성 (public/private 모두 가능)
2. 이 코드들을 저장소에 업로드

### 2. GitHub Secrets 설정
Repository > Settings > Secrets and variables > Actions에서 다음 secrets 추가:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com
```

### 3. Gmail 앱 비밀번호 생성 (권장)
1. Google 계정 > 보안 > 2단계 인증 활성화
2. 앱 비밀번호 생성
3. 생성된 16자리 비밀번호를 `SENDER_PASSWORD`에 사용

## 📰 뉴스 소스

- **연합뉴스**: 정치 섹션
- **조선일보**: 정치 섹션  
- **중앙일보**: 정치 섹션
- **한겨레**: 정치 섹션
- **경향신문**: 정치 섹션

각 언론사에서 최대 5개씩, 총 20개의 최신 뉴스를 수집합니다.

## ⏰ 실행 시간

- **자동 실행**: 매일 오전 9시 (한국 시간)
- **수동 실행**: GitHub Actions 탭에서 "Run workflow" 버튼 클릭

## 🧪 로컬 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (Linux/Mac)
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@gmail.com"

# 실행
python news_scraper.py
```

## 📧 이메일 형식

HTML 형식으로 다음 정보를 포함합니다:
- 뉴스 제목 (링크)
- 언론사명
- 요약 (200자)
- 발행 시간

## ⚙️ 커스터마이징

### 뉴스 소스 변경
`news_scraper.py`의 `news_sources` 딕셔너리를 수정하여 다른 RSS 피드 추가/제거 가능

### 실행 시간 변경
`.github/workflows/daily-news.yml`의 cron 표현식 수정:
```yaml
# 오전 8시: '0 23 * * *'
# 오후 1시: '0 4 * * *'
```

### 이메일 템플릿 수정
`create_html_email()` 메서드에서 HTML 스타일 및 구조 변경 가능

## 🔧 문제해결

### 이메일 전송 실패
1. Gmail 앱 비밀번호 올바른지 확인
2. 2단계 인증 활성화 여부 확인
3. GitHub Secrets 오타 확인

### 뉴스 수집 실패
1. RSS 피드 URL이 변경되었는지 확인
2. 네트워크 연결 상태 확인
3. GitHub Actions 로그 확인

## 📝 라이선스

MIT License
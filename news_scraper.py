import requests
import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
from dateutil import parser
import re
from difflib import SequenceMatcher

class KoreanNewsClipping:
    def __init__(self):
        self.news_sources = {
            "연합뉴스": "https://www.yna.co.kr/rss/politics.xml",  # 정치 RSS로 변경
            "SBS": "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADER",
            "MBC": "https://imnews.imbc.com/rss/google_news/narrativeNews.rss",
            "JTBC": "https://fs.jtbc.co.kr//RSS/politics.xml",
            "KBS": "http://world.kbs.co.kr/rss/rss_news.htm?lang=k&id=po"  # KBS 정치 RSS
        }
        
        # 정치 관련 키워드 (포함되어야 할 키워드)
        self.political_keywords = [
            '정치', '국정감사', '국회', '의원', '대통령', '총리', '장관', '정부', '정당', 
            '여당', '야당', '민주당', '국민의힘', '선거', '투표', '개헌', '법안', '정책',
            '윤석열', '이재명', '한동훈', '조국', '안철수', '김건희', '국정농단',
            '탄핵', '수사', '검찰', '정치인', '공직자', '청와대', '국무총리', '정치권',
            '정치적', '정치인', '정치판', '정세', '정국', '정치현실', '정치적 갈등',
            '대통령실', '여야', '협치', '정치개혁', '정치제도', '국정운영', '국정과제'
        ]
        
        # 제외할 키워드 (이런 키워드가 있으면 제외)
        self.exclude_keywords = [
            'BTS', '방탄소년단', '블랙핑크', '트와이스', '아이유', '연예인', '배우', '가수',
            '드라마', '영화', '예능', 'K-pop', '케이팝', '아이돌', '음악', '콘서트', '앨범',
            '스포츠', '축구', '야구', '농구', '올림픽', '월드컵', '경기', '선수', '코치',
            '날씨', '기상', '태풍', '지진', '화재', '교통사고', '사건사고', '부동산',
            '집값', '아파트', '경제지표', '주식', '코스피', '환율', '금리', '증시',
            '코로나', '백신', '의료', '병원', '질병', '치료', '보건', '의학',
            '교육', '학교', '대학', '입시', '수능', '학생', '교사', '학원',
            '문화', '축제', '전시', '박물관', '미술관', '도서', '책', '작가'
        ]
        
    def similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    def is_political_news(self, title, summary):
        """제목과 요약을 바탕으로 정치 뉴스인지 판단"""
        text = (title + ' ' + summary).lower()
        
        # 제외 키워드가 있으면 정치 뉴스가 아님
        for exclude_word in self.exclude_keywords:
            if exclude_word.lower() in text:
                return False
        
        # 정치 키워드가 있으면 정치 뉴스
        for political_word in self.political_keywords:
            if political_word.lower() in text:
                return True
        
        return False
    
    def remove_duplicates(self, news_list):
        unique_news = []
        
        for news in news_list:
            is_duplicate = False
            current_title = self.clean_html(news['title']).strip()
            
            for existing in unique_news:
                existing_title = self.clean_html(existing['title']).strip()
                
                # 제목 유사도가 80% 이상이면 중복으로 판단
                if self.similarity(current_title, existing_title) >= 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(news)
                
        return unique_news
        
    def fetch_news(self):
        balanced_news = []
        
        for source_name, rss_url in self.news_sources.items():
            try:
                print(f"Fetching from {source_name}...")
                feed = feedparser.parse(rss_url)
                
                if not feed.entries:
                    print(f"No entries found for {source_name}")
                    continue
                    
                # 각 언론사에서 정치 뉴스만 필터링하여 수집
                source_news = []
                for entry in feed.entries:  # 모든 기사를 확인 (개수 제한 제거)
                    title = entry.title
                    summary = entry.get('summary', '')
                    
                    # 정치 뉴스인지 확인
                    if self.is_political_news(title, summary):
                        # 요약 텍스트를 안전하게 처리
                        clean_summary = self.clean_html(summary) if summary else ''
                        # 요약이 너무 길면 자르고 말줄임표 추가
                        if len(clean_summary) > 150:
                            clean_summary = clean_summary[:150] + '...'
                        
                        news_item = {
                            'source': source_name,
                            'title': self.clean_html(title),
                            'link': entry.link,
                            'published': entry.get('published', ''),
                            'summary': clean_summary
                        }
                        source_news.append(news_item)
                        
                        # 각 언론사에서 정확히 5개 수집하면 중단
                        if len(source_news) >= 5:
                            break
                
                # 중복 제거는 하지 않고 바로 추가 (이미 5개로 제한됨)
                balanced_news.extend(source_news)
                
                print(f"Added {len(source_news)} articles from {source_name}")
                
            except Exception as e:
                print(f"Error fetching from {source_name}: {e}")
                
        # 최신 순 정렬
        return sorted(balanced_news, key=lambda x: x.get('published', ''), reverse=True)

    def clean_html(self, text):
        if not text:
            return ""
        
        # HTML 태그 제거
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        
        # HTML 엔티티 디코딩
        import html
        text = html.unescape(text)
        
        # 특수 문자와 공백 정리
        text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
        text = re.sub(r'[\r\n\t]', ' ', text)  # 줄바꿈, 탭을 공백으로
        
        # 특수 기호 제거 (박스, 화살표 등)
        text = re.sub(r'[▲▼◆■□▶◀●○◇◈※★☆♠♣♥♦]', '', text)
        
        # 연속된 특수문자나 점들 정리
        text = re.sub(r'\.{3,}', '...', text)  # 3개 이상의 점을 ...으로
        text = re.sub(r'-{2,}', '--', text)    # 2개 이상의 대시를 --로
        
        return text.strip()
    
    def safe_html_text(self, text):
        """HTML에 안전하게 삽입할 수 있도록 텍스트 처리"""
        if not text:
            return ""
        
        # 먼저 HTML 정리
        text = self.clean_html(text)
        
        # HTML 특수문자 이스케이프
        import html
        text = html.escape(text)
        
        return text
    
    def convert_to_kst(self, timestamp_str):
        try:
            if not timestamp_str:
                return datetime.now(pytz.timezone('Asia/Seoul')).strftime('%m-%d %H:%M')
                
            # Parse the timestamp
            dt = parser.parse(timestamp_str)
            
            # Convert to KST
            kst = pytz.timezone('Asia/Seoul')
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            
            kst_time = dt.astimezone(kst)
            return kst_time.strftime('%m-%d %H:%M')
        except:
            return datetime.now(pytz.timezone('Asia/Seoul')).strftime('%m-%d %H:%M')

    def create_html_email(self, news_list):
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Malgun Gothic', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    .container {{ background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                    .header h2 {{ margin: 0; font-size: 24px; }}
                    .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
                    
                    table {{ 
                        width: 100%; 
                        border-collapse: collapse; 
                        border: 2px solid #333;
                        background-color: white;
                    }}
                    th {{ 
                        padding: 12px; 
                        text-align: left; 
                        font-weight: bold; 
                        border: 2px solid #333;
                        font-size: 14px;
                        color: white;
                    }}
                    .th-title {{ background-color: #2563eb; }}     /* 제목 - 파란색 */
                    .th-content {{ background-color: #16a34a; }}   /* 내용 - 초록색 */
                    .th-source {{ background-color: #ea580c; }}    /* 언론사 - 주황색 */
                    .th-time {{ background-color: #9333ea; }}      /* 시간 - 보라색 */
                    
                    td {{ 
                        padding: 12px; 
                        border: 2px solid #333; 
                        vertical-align: top; 
                    }}
                    .td-even {{ background-color: #f8fafc; }}
                    .td-odd {{ background-color: white; }}
                    
                    .title {{ font-weight: bold; }}
                    .title a {{ text-decoration: none; color: #333; }}
                    .title a:hover {{ color: #007bff; text-decoration: underline; }}
                    
                    .source {{ 
                        display: inline-block;
                        background-color: #e9ecef; 
                        color: #495057; 
                        padding: 4px 8px; 
                        border-radius: 12px; 
                        font-size: 12px; 
                        font-weight: bold;
                    }}
                    
                    .time {{ 
                        color: #6c757d; 
                        font-size: 12px; 
                        font-weight: normal;
                    }}
                    
                    .summary {{ 
                        color: #666; 
                        font-size: 14px; 
                        line-height: 1.4;
                    }}
                    
                    .footer {{ 
                        background-color: #f8f9fa; 
                        padding: 15px; 
                        text-align: center; 
                        color: #6c757d; 
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🗞️ 한국 정치 뉴스 클리핑</h2>
                        <p>{today} | 총 {len(news_list)}개 기사</p>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; border: 2px solid #333; background-color: white;">
                        <thead>
                            <tr>
                                <th style="background-color: #4a4a4a; color: white; padding: 12px; text-align: left; font-weight: bold; border: 2px solid #333; font-size: 14px;" width="40%">제목</th>
                                <th style="background-color: #4a4a4a; color: white; padding: 12px; text-align: left; font-weight: bold; border: 2px solid #333; font-size: 14px;" width="35%">내용</th>
                                <th style="background-color: #4a4a4a; color: white; padding: 12px; text-align: left; font-weight: bold; border: 2px solid #333; font-size: 14px;" width="15%">언론사</th>
                                <th style="background-color: #4a4a4a; color: white; padding: 12px; text-align: left; font-weight: bold; border: 2px solid #333; font-size: 14px;" width="10%">시간</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for i, news in enumerate(news_list, 1):
            kst_time = self.convert_to_kst(news['published'])
            bg_color = "#f8fafc" if i % 2 == 0 else "white"
            
            html += f"""
                            <tr>
                                <td style="padding: 12px; border: 2px solid #333; vertical-align: top; background-color: {bg_color}; font-weight: bold;">
                                    <a href="{news['link']}" target="_blank" style="text-decoration: none; color: #333;">{self.safe_html_text(news['title'])}</a>
                                </td>
                                <td style="padding: 12px; border: 2px solid #333; vertical-align: top; background-color: {bg_color}; color: #666; font-size: 14px; line-height: 1.4;">{self.safe_html_text(news['summary'])}</td>
                                <td style="padding: 12px; border: 2px solid #333; vertical-align: top; background-color: {bg_color};">
                                    <span style="display: inline-block; background-color: #e9ecef; color: #495057; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{self.safe_html_text(news['source'])}</span>
                                </td>
                                <td style="padding: 12px; border: 2px solid #333; vertical-align: top; background-color: {bg_color}; color: #6c757d; font-size: 12px;">{kst_time}</td>
                            </tr>
            """
        
        html += f"""
                        </tbody>
                    </table>
                    
                    <div class="footer">
                        📧 한국 정치 뉴스 자동 클리핑 시스템 | 매일 오전 9시 발송<br>
                        🤖 Generated with Claude Code
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html

    def send_email(self, html_content, recipient_email):
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        try:
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        except ValueError:
            smtp_port = 587
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')
        
        if not all([sender_email, sender_password, recipient_email]):
            # 로컬 테스트용으로 파일 저장
            filename = f"news_clip_{datetime.now().strftime('%Y%m%d')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"뉴스 클리핑을 {filename}에 저장했습니다!")
            return
        
        msg = MIMEMultipart('alternative')
        # Show both execution time and KST time for debugging
        exec_timestamp = datetime.now().strftime('%Y.%m.%d %H:%M')
        kst_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y.%m.%d %H:%M KST')
        msg['Subject'] = f"한국 정치 뉴스 클리핑 - 실행시각: {exec_timestamp} | KST: {kst_time}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 중복 전송 방지를 위한 고유 ID
        unique_id = f"news-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        msg['Message-ID'] = f"<{unique_id}@korean-news-clipper>"
        
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            print("이메일 전송 완료!")
        except Exception as e:
            print(f"이메일 전송 실패: {e}")
            # 실패 시 파일로 저장
            filename = f"news_clip_{datetime.now().strftime('%Y%m%d')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"대신 파일로 저장했습니다: {filename}")

def main():
    scraper = KoreanNewsClipping()
    
    try:
        print("뉴스를 수집하는 중...")
        news_list = scraper.fetch_news()
        
        if not news_list:
            print("수집된 뉴스가 없습니다.")
            return
            
        print(f"총 {len(news_list)}개의 뉴스를 수집했습니다.")
        
        html_content = scraper.create_html_email(news_list)
        
        recipient_email = os.environ.get('RECIPIENT_EMAIL')
        scraper.send_email(html_content, recipient_email)
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
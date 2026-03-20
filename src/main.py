import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QTextEdit, 
                             QPushButton, QFrame, QSplitter, QProgressBar,
                             QInputDialog, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from styles import get_theme_css
from crawler import NaverNewsCrawler
from analyzer import NewsAnalyzer
from config_manager import ConfigManager

class AnalysisThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, analyzer, article, comments):
        super().__init__()
        self.analyzer = analyzer
        self.article = article
        self.comments = comments

    def run(self):
        result = self.analyzer.analyze_opinion(self.article, self.comments)
        self.finished.emit(result)

class ModernNewsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_mgr = ConfigManager(config_path="../config.dat", key_path="../.secret.key")
        self.crawler = NaverNewsCrawler()
        self.analyzer = NewsAnalyzer(api_key=self.config_mgr.get("groq_api_key"))
        self.current_news_list = []
        self.theme = self.config_mgr.get("theme", "dark")
        
        self.setWindowTitle("Newspiko - 고성능 여론 분석 에이전트")
        self.resize(1400, 900)
        self.init_ui()
        self.apply_styles()
        self.load_news()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 사이드바
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(380)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        header_layout = QHBoxLayout()
        sidebar_title = QLabel("Newspiko Feed")
        sidebar_title.setObjectName("sidebarTitle")
        header_layout.addWidget(sidebar_title)
        
        self.api_btn = QPushButton("API")
        self.api_btn.setFixedWidth(50)
        self.api_btn.clicked.connect(self.set_api_key)
        header_layout.addWidget(self.api_btn)
        
        self.theme_btn = QPushButton("◑")
        self.theme_btn.setFixedWidth(40)
        self.theme_btn.setObjectName("themeToggle")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)
        
        sidebar_layout.addLayout(header_layout)

        self.news_list_widget = QListWidget()
        self.news_list_widget.itemClicked.connect(self.on_news_selected)
        sidebar_layout.addWidget(self.news_list_widget)
        
        self.refresh_btn = QPushButton("피드 새로고침")
        self.refresh_btn.clicked.connect(self.load_news)
        sidebar_layout.addWidget(self.refresh_btn)

        # 본문 및 상세 영역 (3분할 스플리터)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. 기사 본문 영역
        article_frame = QFrame()
        article_layout = QVBoxLayout(article_frame)
        self.title_label = QLabel("기사를 선택해 주세요")
        self.title_label.setObjectName("articleTitle")
        self.title_label.setWordWrap(True)
        article_layout.addWidget(self.title_label)

        self.article_view = QTextEdit()
        self.article_view.setReadOnly(True)
        self.article_view.setObjectName("articleView")
        article_layout.addWidget(self.article_view)
        
        main_splitter.addWidget(article_frame)

        # 2. 오른쪽 영역 (댓글 + 분석)
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # 댓글 리스트 영역
        comment_frame = QFrame()
        comment_layout = QVBoxLayout(comment_frame)
        comment_title = QLabel("수집된 전체 댓글")
        comment_title.setObjectName("commentTitle")
        comment_layout.addWidget(comment_title)
        
        self.comment_list_widget = QListWidget()
        self.comment_list_widget.setObjectName("commentList")
        comment_layout.addWidget(self.comment_list_widget)
        right_splitter.addWidget(comment_frame)

        # 분석 결과 영역
        analysis_frame = QFrame()
        analysis_layout = QVBoxLayout(analysis_frame)
        
        analysis_header = QHBoxLayout()
        analysis_label = QLabel("AI 여론 통찰")
        analysis_label.setObjectName("analysisLabel")
        analysis_header.addWidget(analysis_label)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximum(0)
        analysis_header.addWidget(self.progress)
        analysis_layout.addLayout(analysis_header)
        
        self.analysis_view = QTextEdit()
        self.analysis_view.setReadOnly(True)
        self.analysis_view.setObjectName("analysisView")
        analysis_layout.addWidget(self.analysis_view)
        
        right_splitter.addWidget(analysis_frame)
        main_splitter.addWidget(right_splitter)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(main_splitter)

    def apply_styles(self):
        self.setStyleSheet(get_theme_css(self.theme))

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.config_mgr.set("theme", self.theme)
        self.apply_styles()

    def set_api_key(self):
        current_key = self.config_mgr.get("groq_api_key", "")
        key, ok = QInputDialog.getText(self, "API Key", "Groq API Key를 입력하세요:", text=current_key)
        if ok and key:
            self.config_mgr.set("groq_api_key", key)
            self.analyzer = NewsAnalyzer(api_key=key)
            QMessageBox.information(self, "완료", "API 키가 안전하게 저장되었습니다.")

    def load_news(self):
        self.statusBar().showMessage("뉴스 불러오는 중...")
        self.news_list_widget.clear()
        self.current_news_list = self.crawler.get_ranking_news()
        
        for news in self.current_news_list:
            item_text = f"[{news['press']}] {news['title']}"
            self.news_list_widget.addItem(item_text)
        
        self.statusBar().showMessage(f"총 {len(self.current_news_list)}개의 기사를 로드했습니다.")

    def on_news_selected(self, item):
        idx = self.news_list_widget.row(item)
        news = self.current_news_list[idx]
        
        self.title_label.setText(news['title'])
        self.article_view.setHtml("<p style='color: #60a5fa;'>데이터 수집 중...</p>")
        self.analysis_view.setText("기사를 선택하면 분석이 시작됩니다.")
        self.comment_list_widget.clear()
        
        # 상세 데이터 수집
        details = self.crawler.get_article_details(news['link'])
        # 기사 본문 프리티 프린트 (HTML 적용)
        formatted_content = details['content'].replace("\n", "<br>")
        self.article_view.setHtml(f"""
            <div style='line-height: 1.8; font-size: 16px; color: #cbd5e1;'>
                {formatted_content}
            </div>
        """)
        
        self.statusBar().showMessage("댓글 수집 중...")
        comments = self.crawler.get_comments(details['oid'], details['aid'])
        self.statusBar().showMessage(f"댓글 {len(comments)}개 수집 완료")

        # 댓글 리스트 프리티 프린트
        for c in comments:
            comment_item = QListWidgetItem()
            self.comment_list_widget.addItem(comment_item)
            
            # 사용자 정의 위젯 대신 텍스트 서식 활용 (가독성 최우선)
            display_text = f"👤 {c['user']} | 🕒 {c['time']}\n{c['text']}\n👍 {c['good']}  👎 {c['bad']}"
            comment_item.setText(display_text)
            comment_item.setToolTip(c['text'])

        if not self.analyzer.api_key:
            self.analysis_view.setText("Groq API 키가 설정되지 않았습니다.")
            return

        self.progress.setVisible(True)
        self.analysis_view.setText("Newspiko AI 분석 엔진 가동 중...")
        
        self.thread = AnalysisThread(self.analyzer, {'title': news['title'], 'content': details['content']}, comments)
        self.thread.finished.connect(self.on_analysis_finished)
        self.thread.start()

    def on_analysis_finished(self, result):
        self.progress.setVisible(False)
        self.analysis_view.setMarkdown(result)
        self.statusBar().showMessage("분석 완료")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernNewsApp()
    window.show()
    sys.exit(app.exec())

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QTextEdit, 
                             QPushButton, QFrame, QSplitter, QProgressBar,
                             QInputDialog, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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
        self.config_mgr = ConfigManager()
        self.crawler = NaverNewsCrawler()
        self.analyzer = NewsAnalyzer(api_key=self.config_mgr.get("groq_api_key"))
        self.current_news_list = []
        
        self.setWindowTitle("NAVER News Insight v1.0")
        self.resize(1300, 850)
        self.init_ui()
        self.apply_styles()
        self.load_news()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 사이드바
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(380)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        header_layout = QHBoxLayout()
        sidebar_title = QLabel("실시간 랭킹 뉴스")
        sidebar_title.setObjectName("sidebarTitle")
        header_layout.addWidget(sidebar_title)
        
        self.api_btn = QPushButton("API 설정")
        self.api_btn.setFixedWidth(80)
        self.api_btn.clicked.connect(self.set_api_key)
        header_layout.addWidget(self.api_btn)
        sidebar_layout.addLayout(header_layout)

        self.news_list_widget = QListWidget()
        self.news_list_widget.itemClicked.connect(self.on_news_selected)
        sidebar_layout.addWidget(self.news_list_widget)
        
        self.refresh_btn = QPushButton("뉴스 새로고침")
        self.refresh_btn.clicked.connect(self.load_news)
        sidebar_layout.addWidget(self.refresh_btn)

        # 본문 및 분석 영역
        splitter = QSplitter(Qt.Orientation.Vertical)

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
        
        splitter.addWidget(article_frame)

        # 2. 분석 결과 영역
        analysis_frame = QFrame()
        analysis_layout = QVBoxLayout(analysis_frame)
        
        analysis_header = QHBoxLayout()
        analysis_label = QLabel("AI 여론 분석 및 조작 탐지")
        analysis_label.setObjectName("analysisLabel")
        analysis_header.addWidget(analysis_label)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximum(0) # Busy indicator
        analysis_header.addWidget(self.progress)
        analysis_layout.addLayout(analysis_header)
        
        self.analysis_view = QTextEdit()
        self.analysis_view.setReadOnly(True)
        self.analysis_view.setObjectName("analysisView")
        analysis_layout.addWidget(self.analysis_view)
        
        splitter.addWidget(analysis_frame)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(splitter)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#main_widget { background-color: #0f172a; }
            QFrame { background-color: #1e293b; border: none; border-radius: 8px; margin: 5px; }
            #sidebarTitle { color: #38bdf8; font-size: 18px; font-weight: bold; }
            #analysisLabel { color: #10b981; font-size: 18px; font-weight: bold; }
            #articleTitle { color: #f8fafc; font-size: 20px; font-weight: bold; padding: 10px; }
            QListWidget { background-color: transparent; border: 1px solid #334155; color: #94a3b8; font-size: 14px; border-radius: 5px; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #334155; }
            QListWidget::item:selected { background-color: #334155; color: #38bdf8; border-left: 5px solid #38bdf8; }
            QTextEdit { background-color: #111827; color: #e2e8f0; border: 1px solid #334155; font-size: 15px; border-radius: 5px; }
            QPushButton { background-color: #38bdf8; color: #0f172a; border-radius: 5px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #7dd3fc; }
            QProgressBar { height: 4px; border: none; background: #334155; }
            QProgressBar::chunk { background: #38bdf8; }
        """)

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
        self.article_view.setText("데이터 수집 중...")
        self.analysis_view.setText("기사를 선택하면 분석이 시작됩니다.")
        
        # 상세 데이터 수집 (본문 + 댓글)
        details = self.crawler.get_article_details(news['link'])
        self.article_view.setText(details['content'] or "본문을 가져올 수 없습니다.")
        
        comments = self.crawler.get_comments(details['oid'], details['aid'])
        
        if not self.analyzer.api_key:
            self.analysis_view.setText("Groq API 키가 설정되지 않았습니다. 우측 상단의 'API 설정' 버튼을 이용해 주세요.")
            return

        # 분석 스레드 실행
        self.progress.setVisible(True)
        self.analysis_view.setText("AI 분석 엔진 가동 중... 잠시만 기다려 주세요.")
        
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

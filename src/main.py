import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QTextEdit, 
                             QPushButton, QFrame, QSplitter, QProgressBar,
                             QInputDialog, QMessageBox, QListWidgetItem, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from styles import get_theme_css
from crawler import NaverNewsCrawler
from crawler_daum import DaumNewsCrawler
from analyzer import NewsAnalyzer
from config_manager import ConfigManager

class AnalysisThread(QThread):
    finished = pyqtSignal(dict) # 결과와 감성 점수를 함께 전달
    
    def __init__(self, analyzer, article, comments):
        super().__init__()
        self.analyzer = analyzer
        self.article = article
        self.comments = comments

    def run(self):
        result = self.analyzer.analyze_opinion(self.article, self.comments)
        # 간단한 감성 분석 파싱 (결과 텍스트에서 긍정/부정 수치를 찾아냄 - 모의)
        sentiment = {"pos": 50, "neg": 50}
        if "긍정" in result: sentiment["pos"] += 20; sentiment["neg"] -= 20
        elif "부정" in result: sentiment["neg"] += 20; sentiment["pos"] -= 20
        self.finished.emit({"text": result, "sentiment": sentiment})

class ModernNewsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_mgr = ConfigManager(config_path="../config.dat", key_path="../.secret.key")
        self.naver_crawler = NaverNewsCrawler()
        self.daum_crawler = DaumNewsCrawler()
        self.crawler = self.naver_crawler
        
        self.analyzer = NewsAnalyzer(api_key=self.config_mgr.get("groq_api_key"))
        self.current_news_list = []
        self.theme = self.config_mgr.get("theme", "dark")
        self.agentic_active = self.config_mgr.get("agentic_active", False)
        
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
        
        # 상단 헤더
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

        # 소스 선택 및 에이전틱 모드 패널
        control_panel = QFrame()
        control_panel.setObjectName("agenticHeader")
        control_layout = QVBoxLayout(control_panel)
        
        source_layout = QHBoxLayout()
        source_label = QLabel("뉴스 소스:")
        source_label.setStyleSheet("font-weight: bold; color: var(--color-text-dim);")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Naver News", "Daum News"])
        self.source_combo.currentIndexChanged.connect(self.on_source_changed)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_combo)
        control_layout.addLayout(source_layout)
        
        self.agentic_cb = QCheckBox("Agentic Mode")
        self.agentic_cb.setChecked(self.agentic_active)
        self.agentic_cb.toggled.connect(self.toggle_agentic)
        control_layout.addWidget(self.agentic_cb)
        
        self.agentic_status = QLabel("사용자 수동 제어 모드")
        self.agentic_status.setObjectName("agenticStatus")
        if self.agentic_active:
            self.agentic_status.setText("● AI 자동 분석 활성화됨")
        control_layout.addWidget(self.agentic_status)
        
        sidebar_layout.addWidget(control_panel)

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
        
        comment_header = QHBoxLayout()
        comment_title = QLabel("수집된 전체 댓글")
        comment_title.setObjectName("commentTitle")
        comment_header.addWidget(comment_title)
        
        self.pattern_label = QLabel("") # 패턴 분석 결과용
        self.pattern_label.setStyleSheet("color: #fbbf24; font-size: 11px;")
        comment_header.addWidget(self.pattern_label)
        comment_layout.addLayout(comment_header)
        
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

        # 감성 시각화 바 추가
        self.sentiment_container = QFrame()
        self.sentiment_container.setFixedHeight(20)
        self.sentiment_container.setVisible(False)
        self.sent_layout = QHBoxLayout(self.sentiment_container)
        self.sent_layout.setContentsMargins(0, 0, 0, 0)
        self.sent_layout.setSpacing(0)
        self.pos_bar = QLabel()
        self.pos_bar.setStyleSheet("background-color: #3b82f6; border-top-left-radius: 4px; border-bottom-left-radius: 4px;")
        self.neg_bar = QLabel()
        self.neg_bar.setStyleSheet("background-color: #ef4444; border-top-right-radius: 4px; border-bottom-right-radius: 4px;")
        self.sent_layout.addWidget(self.pos_bar, 50)
        self.sent_layout.addWidget(self.neg_bar, 50)
        analysis_layout.addWidget(self.sentiment_container)
        
        # 키워드 마인드맵/태그 영역 추가
        self.keyword_frame = QFrame()
        self.keyword_frame.setObjectName("keywordFrame")
        self.keyword_frame.setVisible(False)
        self.keyword_layout = QHBoxLayout(self.keyword_frame)
        self.keyword_layout.setContentsMargins(5, 5, 5, 5)
        self.keyword_layout.setSpacing(5)
        analysis_layout.addWidget(self.keyword_frame)
        
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

    def on_source_changed(self, index):
        if index == 0:
            self.crawler = self.naver_crawler
        else:
            self.crawler = self.daum_crawler
        self.load_news()

    def toggle_agentic(self, checked):
        self.agentic_active = checked
        self.config_mgr.set("agentic_active", checked)
        if checked:
            self.agentic_status.setText("● AI 자동 분석 활성화됨")
            if self.news_list_widget.count() > 0:
                self.news_list_widget.setCurrentRow(0)
                self.on_news_selected(self.news_list_widget.item(0))
        else:
            self.agentic_status.setText("사용자 수동 제어 모드")

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
        self.statusBar().showMessage(f"{self.source_combo.currentText()} 뉴스 불러오는 중...")
        self.news_list_widget.clear()
        self.current_news_list = self.crawler.get_ranking_news()
        
        for news in self.current_news_list:
            item_text = f"[{news['press']}] {news['title']}"
            self.news_list_widget.addItem(item_text)
        
        self.statusBar().showMessage(f"총 {len(self.current_news_list)}개의 기사를 로드했습니다.")
        
        # 에이전틱 모드일 경우 첫 번째 기사 자동 선택/분석
        if self.agentic_active and self.news_list_widget.count() > 0:
            self.news_list_widget.setCurrentRow(0)
            self.on_news_selected(self.news_list_widget.item(0))

    def on_news_selected(self, item):
        idx = self.news_list_widget.row(item)
        news = self.current_news_list[idx]
        
        self.title_label.setText(news['title'])
        self.article_view.setHtml("<p style='color: #60a5fa;'>데이터 수집 중...</p>")
        self.analysis_view.setText("기사를 선택하면 분석이 시작됩니다.")
        self.comment_list_widget.clear()
        self.sentiment_container.setVisible(False)
        self.pattern_label.setText("")
        
        # 상세 데이터 수집
        details = self.crawler.get_article_details(news['link'])
        
        # 테마에 따른 기사 텍스트 색상 결정 (라이트 모드일 때 검정색)
        text_color = "#000000" if self.theme == "light" else "#cbd5e1"
        
        # 기사 본문 프리티 프린트 (HTML 적용)
        formatted_content = details['content'].replace("\n", "<br>")
        self.article_view.setHtml(f"""
            <div style='line-height: 1.8; font-size: 16px; color: {text_color};'>
                {formatted_content}
            </div>
        """)
        
        self.statusBar().showMessage("댓글 수집 중...")
        comments = self.crawler.get_comments(details['oid'], details['aid'])
        self.statusBar().showMessage(f"댓글 {len(comments)}개 수집 완료")

        # 패턴 분석 (집단성 탐지 고도화)
        from pattern_detector import PatternDetector
        detector = PatternDetector()
        analysis = detector.analyze(comments)
        
        heavy_users = analysis['heavy_users']
        macro_count = len(analysis['macro_comments'])
        similar_count = len(analysis['similar_groups'])
        
        status_msg = []
        if heavy_users: status_msg.append(f"중복유저 {len(heavy_users)}명")
        if macro_count: status_msg.append(f"매크로의심 {macro_count}건")
        if similar_count: status_msg.append(f"집단유사성 {similar_count}건")
        
        if status_msg:
            self.pattern_label.setText("⚠ " + " | ".join(status_msg))
        else:
            self.pattern_label.setText("✓ 특이 패턴 미감지")

        # 댓글 리스트 프리티 프린트
        for c in comments:
            comment_item = QListWidgetItem()
            self.comment_list_widget.addItem(comment_item)
            
            display_text = f"👤 {c['user']} | 🕒 {c['time']}\n{c['text']}\n👍 {c['good']}  👎 {c['bad']}"
            comment_item.setText(display_text)
            
            # 중복 작성자 강조 스타일
            if c['user'] in heavy_users:
                comment_item.setBackground(Qt.GlobalColor.darkYellow if self.theme=="dark" else Qt.GlobalColor.yellow)

            comment_item.setToolTip("클릭하여 이 댓글에 대한 상세 분석을 수행합니다.")
            comment_item.setData(Qt.ItemDataRole.UserRole, c['text']) # 원본 텍스트 저장

        # 댓글 클릭 이벤트 연결
        try:
            self.comment_list_widget.itemDoubleClicked.disconnect()
        except: pass
        self.comment_list_widget.itemDoubleClicked.connect(self.on_comment_double_clicked)

        if not self.analyzer.api_key:
            self.analysis_view.setText("Groq API 키가 설정되지 않았습니다.")
            return

        self.progress.setVisible(True)
        self.analysis_view.setText("Newspiko AI 분석 엔진 가동 중...")
        
        self.thread = AnalysisThread(self.analyzer, {'title': news['title'], 'content': details['content']}, comments)
        self.thread.finished.connect(self.on_analysis_finished)
        self.thread.start()

    def on_comment_double_clicked(self, item):
        comment_text = item.data(Qt.ItemDataRole.UserRole)
        self.statusBar().showMessage(f"댓글 분석 선택됨: {comment_text[:20]}...")
        QMessageBox.information(self, "댓글 상세", f"선택한 댓글 원문:\n\n{comment_text}")

    def on_analysis_finished(self, data):
        self.progress.setVisible(False)
        result_text = data["text"]
        
        # 키워드 파싱 및 표시
        import re
        kw_match = re.search(r'\[KEYWORDS:\s*(.*?)\]', result_text)
        if kw_match:
            try:
                # JSON 형식이거나 단순 쉼표 구분일 수 있음
                kw_str = kw_match.group(1).replace("'", '"')
                import json
                keywords = json.loads(kw_str) if kw_str.startswith('[') else [k.strip() for k in kw_str.split(',')]
                
                # 기존 키워드 제거
                for i in reversed(range(self.keyword_layout.count())): 
                    self.keyword_layout.itemAt(i).widget().setParent(None)
                
                for kw in keywords[:8]: # 최대 8개
                    kw_label = QLabel(f" #{kw} ")
                    kw_label.setStyleSheet("""
                        background-color: #334155; color: #38bdf8; 
                        border-radius: 10px; padding: 2px 8px; font-weight: bold; font-size: 11px;
                    """)
                    self.keyword_layout.addWidget(kw_label)
                self.keyword_frame.setVisible(True)
                
                # 본문에서 키워드 태그 제거 (UI 깔끔하게)
                result_text = result_text.replace(kw_match.group(0), "")
            except:
                self.keyword_frame.setVisible(False)
        else:
            self.keyword_frame.setVisible(False)

        self.analysis_view.setMarkdown(result_text)
        
        # 감성 시각화 업데이트
        sent = data["sentiment"]
        self.pos_bar.setToolTip(f"긍정 지표: {sent['pos']}%")
        self.neg_bar.setToolTip(f"부정 지표: {sent['neg']}%")
        self.sent_layout.setStretch(0, sent["pos"])
        self.sent_layout.setStretch(1, sent["neg"])
        self.sentiment_container.setVisible(True)
        
        self.statusBar().showMessage("분석 완료")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernNewsApp()
    window.show()
    sys.exit(app.exec())

def get_theme_css(theme="dark"):
    if theme == "dark":
        vars = {
            "--color-bg": "#0b0f19",
            "--color-surface": "#161e2b",
            "--color-surface-low": "#0f172a",
            "--color-border": "#232d3d",
            "--color-primary": "#2563eb",
            "--color-primary-hover": "#3b82f6",
            "--color-text": "#f8fafc",
            "--color-text-dim": "#94a3b8",
            "--color-accent": "#34d399",
            "--color-error": "#ef4444",
            "--color-pos": "#10b981", # Positive (Emerald 500)
            "--color-neg": "#ef4444", # Negative (Red 500)
            "--color-neu": "#94a3b8", # Neutral (Slate 400)
            "--color-scroll-bg": "#0f172a",
            "--color-scroll-handle": "#334155"
        }
    else:
        vars = {
            "--color-bg": "#f1f5f9",
            "--color-surface": "#ffffff",
            "--color-surface-low": "#e2e8f0",
            "--color-border": "#cbd5e1",
            "--color-primary": "#2563eb",
            "--color-primary-hover": "#1d4ed8",
            "--color-text": "#000000",
            "--color-text-dim": "#334155",
            "--color-accent": "#059669",
            "--color-error": "#dc2626",
            "--color-pos": "#059669",
            "--color-neg": "#dc2626",
            "--color-neu": "#64748b",
            "--color-agentic": "#8b5cf6",
            "--color-scroll-bg": "#f1f5f9",
            "--color-scroll-handle": "#94a3b8"
        }

    # Qt QSS에서 var() 사용을 흉내내기 위해 동적 주입 (Qt natively supports minimal variables since v6, but manual injection is safer for full control)
    css = f"""
    QMainWindow, QWidget {{ 
        background-color: {vars["--color-bg"]}; 
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; 
    }}
    QFrame {{ 
        background-color: {vars["--color-surface"]}; 
        border: 1px solid {vars["--color-border"]}; 
        border-radius: 12px; 
    }}
    #sidebarTitle {{ color: #60a5fa; font-size: 20px; font-weight: 900; letter-spacing: -0.5px; padding: 5px; }}
    #commentTitle, #analysisLabel {{ color: {vars["--color-accent"]}; font-size: 16px; font-weight: bold; padding: 5px; }}
    #articleTitle {{ color: {vars["--color-text"]}; font-size: 24px; font-weight: 800; line-height: 1.4; padding: 10px; margin-bottom: 5px; }}
    
    QListWidget {{ background-color: transparent; border: none; color: {vars["--color-text-dim"]}; outline: none; }}
    QListWidget::item {{ padding: 18px; border-bottom: 1px solid {vars["--color-border"]}; border-radius: 0px; }}
    QListWidget::item:selected {{ background-color: {vars["--color-surface-low"]}; color: #60a5fa; border-left: 4px solid #60a5fa; }}
    
    #commentList::item {{ padding: 12px; background-color: {vars["--color-surface-low"]}; border-radius: 8px; margin-bottom: 6px; border: 1px solid {vars["--color-border"]}; }}
    
    QTextEdit {{ 
        background-color: {vars["--color-surface-low"]}; 
        color: {vars["--color-text-dim"]}; 
        border: none; 
        font-size: 16px; 
        line-height: 1.8; 
        padding: 15px;
    }}
    
    QPushButton {{ 
        background-color: {vars["--color-primary"]}; 
        color: white; 
        border-radius: 8px; 
        padding: 12px; 
        font-weight: bold; 
        font-size: 14px;
    }}
    QPushButton:hover {{ background-color: {vars["--color-primary-hover"]}; }}
    
    #agenticHeader {{
        background-color: {vars["--color-surface-low"]};
        border-bottom: 2px solid {vars.get("--color-agentic", "#8b5cf6")};
        border-radius: 0px;
        padding: 10px;
        margin-bottom: 5px;
    }}
    #agenticStatus {{ color: {vars.get("--color-agentic", "#8b5cf6")}; font-weight: bold; font-size: 13px; }}
    
    QCheckBox {{ color: {vars["--color-text"]}; spacing: 8px; font-weight: bold; }}
    QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid {vars["--color-border"]}; }}
    QCheckBox::indicator:checked {{ background-color: {vars.get("--color-agentic", "#8b5cf6")}; border: 1px solid {vars.get("--color-agentic", "#8b5cf6")}; }}

    #themeToggle {{
        background-color: {vars["--color-surface"]};
        color: {vars["--color-text"]};
        border: 1px solid {vars["--color-border"]};
        padding: 8px;
    }}

    QProgressBar {{ height: 3px; border: none; background: {vars["--color-surface-low"]}; }}
    QProgressBar::chunk {{ background: #60a5fa; }}
    
    QScrollBar:vertical {{
        border: none;
        background: {vars["--color-scroll-bg"]};
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {vars["--color-scroll-handle"]};
        min-height: 20px;
        border-radius: 4px;
    }}
    """
    return css

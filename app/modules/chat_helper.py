from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QScrollArea, QFrame, QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor
from datetime import datetime
from app.services.db_service import db_service
from app.services.chat_engine import ChatEngine


def create_light_palette():
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#FFF9E6"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#FF0000"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#4D96FF"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#FFE082"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    return palette


class ChatHelperModule(QWidget):
    """对话助手模块 - 侧边栏管理会话，主区域显示对话"""

    def __init__(self):
        super().__init__()
        self.chat_engine = ChatEngine()
        self.current_session_id = None
        self.init_ui()

    def init_ui(self):
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")
            app.setPalette(create_light_palette())

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        sidebar = self._create_sidebar()
        layout.addWidget(sidebar)

        main_area = self._create_main_chat_area()
        layout.addWidget(main_area)

        self.setLayout(layout)
        self._create_new_session()

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #FFF9E6;
                border-right: 2px solid #D4C080;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("\U0001f4ac 对话历史")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A1A1A;")
        layout.addWidget(title)

        new_btn = QPushButton("\U0001f534 新建对话")
        new_btn.setMinimumHeight(35)
        new_btn.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #4CAF50;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        new_btn.clicked.connect(self._create_new_session)
        layout.addWidget(new_btn)

        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #D4C080;")
        layout.addWidget(separator)

        self.session_list_scroll = QScrollArea()
        self.session_list_scroll.setWidgetResizable(True)
        self.session_list_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #FFE082;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #D4C080;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #D4C08A;
            }
        """)

        self.session_list_widget = QWidget()
        self.session_list_layout = QVBoxLayout(self.session_list_widget)
        self.session_list_layout.setSpacing(5)
        self.session_list_layout.setContentsMargins(5, 5, 5, 5)

        self.session_list_scroll.setWidget(self.session_list_widget)
        layout.addWidget(self.session_list_scroll)

        layout.addStretch()
        return sidebar

    def _create_main_chat_area(self):
        main = QFrame()
        main.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
        """)

        self.main_layout = QVBoxLayout(main)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        self.chat_title = QLabel("\U0001f916 压力疏导助手")
        self.chat_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A1A1A;")
        header.addWidget(self.chat_title)
        header.addStretch()
        self.main_layout.addLayout(header)

        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #D4C080;")
        self.main_layout.addWidget(separator)

        # 消息显示区域
        self.message_scroll = QScrollArea()
        self.message_scroll.setWidgetResizable(True)
        self.message_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.message_widget = QWidget()
        self.message_layout = QVBoxLayout(self.message_widget)
        self.message_layout.setSpacing(10)
        self.message_layout.setContentsMargins(0, 10, 0, 10)

        self.message_scroll.setWidget(self.message_widget)
        self.main_layout.addWidget(self.message_scroll)

        # 输入区域
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF9E6;
                border: 2px solid #D4C080;
                border-radius: 10px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(5)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("说说你的烦恼，我在这里陪你...")
        self.input_text.setMaximumHeight(100)
        self.input_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                color: #1A1A1A;
                background-color: #FFFFFF;
                border: none;
                padding: 5px;
            }
        """)
        input_layout.addWidget(self.input_text)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        send_btn = QPushButton("\U0001f4e5 发送")
        send_btn.setMinimumHeight(35)
        send_btn.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #2196F3;
                border: none;
                border-radius: 6px;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        send_btn.clicked.connect(self._send_message)
        btn_layout.addWidget(send_btn)

        input_layout.addLayout(btn_layout)
        self.main_layout.addWidget(input_frame)

        return main

    def _create_new_session(self):
        now = datetime.now()
        title = f"新对话 - {now.strftime('%H:%M')}"

        session_id = db_service.create_session(title)
        self.current_session_id = session_id

        self._clear_layout_safe(self.message_layout)

        welcome = QLabel("\U0001f4a1 有什么心事都可以跟我说哦～")
        welcome.setStyleSheet("font-size: 14px; color: #666666; padding: 10px;")
        self.message_layout.addWidget(welcome)

        self._load_session_list()

    def _load_session_list(self):
        self._clear_layout_safe(self.session_list_layout)

        sessions = db_service.get_all_sessions()

        if not sessions:
            empty_label = QLabel("\U0001f4e7 暂无对话\n点击新建对话开始吧！")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                font-size: 13px;
                color: #666666;
                padding: 20px;
                background-color: transparent;
            """)
            self.session_list_layout.addWidget(empty_label)
            return

        for session in sessions:
            session_item = self._create_session_item(session)
            self.session_list_layout.addWidget(session_item)

    def _create_session_item(self, session):
        item = QFrame()
        item.setObjectName(f"session_{session['id']}")
        item.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #D4C080;
                border-radius: 6px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #FFF9E6;
                border-color: #F0C419;
            }
        """)

        item_layout = QHBoxLayout(item)
        item_layout.setSpacing(5)
        item_layout.setContentsMargins(5, 5, 5, 5)

        messages = db_service.get_session_messages(session['id'])
        title_text = session['title']
        if messages:
            user_msgs = [m for m in messages if m['role'] == 'user']
            if user_msgs:
                first_msg = user_msgs[0]['content']
                title_text = first_msg[:30] + ('...' if len(first_msg) > 30 else '')

        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-size: 12px; color: #1A1A1A;")
        title_label.setWordWrap(True)
        title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        title_label.mousePressEvent = lambda e, sid=session['id']: self._open_session(sid)
        item_layout.addWidget(title_label)

        item_layout.addStretch()

        delete_btn = QPushButton("\u2715")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: #999999;
                background-color: transparent;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FF6B6B;
                color: #FFFFFF;
            }
        """)
        delete_btn.clicked.connect(lambda checked, sid=session['id']: self._delete_session(sid))
        item_layout.addWidget(delete_btn)

        return item

    def _open_session(self, session_id):
        self.current_session_id = session_id

        self._clear_layout_safe(self.message_layout)

        messages = db_service.get_session_messages(session_id)

        if not messages:
            welcome = QLabel("\U0001f4a1 有什么心事都可以跟我说哦～")
            welcome.setStyleSheet("font-size: 14px; color: #666666; padding: 10px;")
            self.message_layout.addWidget(welcome)
        else:
            for msg in messages:
                if msg['role'] == 'user':
                    self._add_message_bubble("\U0001f464 " + msg['content'], is_user=True)
                else:
                    self._add_message_bubble("\U0001f916 " + msg['content'], is_user=False)

        self._update_session_selection(session_id)

    def _delete_session(self, session_id):
        if session_id == self.current_session_id:
            QMessageBox.warning(self, "提示", "不能删除当前正在使用的会话")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个对话吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            db_service.delete_session(session_id)
            self._load_session_list()

    def _update_session_selection(self, session_id):
        for i in range(self.session_list_layout.count()):
            widget = self.session_list_layout.itemAt(i).widget()
            if widget and widget.objectName().startswith("session_"):
                sid = int(widget.objectName().split("_")[1])
                bg = "#FFE082" if sid == session_id else "#FFFFFF"
                widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg};
                        border: 1px solid #D4C080;
                        border-radius: 6px;
                        padding: 5px;
                    }}
                    QFrame:hover {{
                        background-color: #FFF9E6;
                        border-color: #F0C419;
                    }}
                """)

    def _send_message(self):
        message = self.input_text.toPlainText().strip()
        if not message:
            return

        self.input_text.setPlainText("")

        self._add_message_bubble("\U0001f464 " + message, is_user=True)
        db_service.add_message(self.current_session_id, "user", message)

        response = self.chat_engine.generate_response(message)
        ai_text = response["response"]
        db_service.add_message(self.current_session_id, "assistant", ai_text)

        QTimer.singleShot(1000, lambda: self._add_ai_response(ai_text))

    def _add_message_bubble(self, text, is_user=False):
        bubble = QLabel(text)
        bg = "#2196F3" if is_user else "#FFF9E6"
        fg = "#FFFFFF" if is_user else "#1A1A1A"
        bubble.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {fg};
                background-color: {bg};
                padding: 8px 12px;
                border-radius: 8px;
            }}
        """)
        bubble.setWordWrap(True)
        self.message_layout.addWidget(bubble)
        self.message_layout.addStretch()

    def _add_ai_response(self, text):
        self._add_message_bubble("\U0001f916 " + text, is_user=False)

    def _clear_layout_safe(self, layout):
        """安全清空布局，防止对象已被删除"""
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child and child.widget():
                    child.widget().deleteLater()
        except Exception:
            pass
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child and child.widget():
                    child.widget().deleteLater()
        except Exception:
            pass

    def cleanup_empty_sessions(self):
        """关闭时清理未发言的新会话"""
        sessions = db_service.get_all_sessions()
        for session in sessions:
            messages = db_service.get_session_messages(session['id'])
            if not messages:
                db_service.delete_session(session['id'])

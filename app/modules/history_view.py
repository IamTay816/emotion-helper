from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QFrame, QDialog, QApplication)
from PyQt6.QtCore import Qt, QDate, QLocale
from PyQt6.QtGui import QFont, QPalette, QColor
from datetime import datetime
from app.services.db_service import db_service
from app.utils.helpers import get_mood_color, format_date_for_display


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


class HistoryViewModule(QWidget):
    """历史记录模块 - 按时间倒序展示所有心情记录"""

    def __init__(self):
        super().__init__()
        self.current_date = datetime.now()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")
            app.setPalette(create_light_palette())

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题栏
        header_layout = QHBoxLayout()

        title_label = QLabel("\U0001f4d6 历史记录")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A1A1A;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        refresh_btn = QPushButton("\U0001f503 刷新")
        refresh_btn.setMinimumHeight(30)
        refresh_btn.setStyleSheet(self._get_small_button_style("#2196F3", "#1976D2"))
        refresh_btn.clicked.connect(self.load_history)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 12px; color: #666666;")
        layout.addWidget(self.stats_label)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #FFF9E6;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #D4C080;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #D4C08A;
            }
        """)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        layout.addStretch()
        self.setLayout(layout)

    def _get_small_button_style(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                font-size: 12px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: {bg_color};
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    def load_history(self):
        self._clear_layout(self.scroll_layout)

        entries = db_service.get_all_mood_entries(limit=500)

        if not entries:
            no_data = QLabel("\U0001f4cb 暂无历史记录\n\n快去记录今天的心情吧！")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data.setStyleSheet("""
                font-size: 16px;
                color: #666666;
                padding: 40px;
                background-color: #FFF9E6;
                border-radius: 10px;
            """)
            self.scroll_layout.addWidget(no_data)
            self.stats_label.setText("共 0 条记录")
            return

        from collections import OrderedDict
        date_groups = OrderedDict()
        for entry in entries:
            d = entry["date"]
            if d not in date_groups:
                date_groups[d] = []
            date_groups[d].append(entry)

        unique_dates = len(date_groups)
        self.stats_label.setText(f"共 {len(entries)} 条记录，覆盖 {unique_dates} 天")

        for date_str, date_entries in date_groups.items():
            card = self._create_record_card(date_str, date_entries)
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def _create_record_card(self, date_str, entries):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #D4C080;
                border-radius: 10px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #F0C419;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # ===== 第一行：日期 + 数量 + 展开按钮 =====
        date_header = QHBoxLayout()

        date_label = QLabel(f"\U0001f4c5 {format_date_for_display(date_str)}")
        date_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A1A1A;")
        date_header.addWidget(date_label)

        date_header.addStretch()

        # 数量标签（纯文本）
        count_label = QLabel(f"({len(entries)}条)")
        count_label.setStyleSheet("font-size: 12px; color: #666666;")
        date_header.addWidget(count_label)

        # 展开/收起按钮
        toggle_btn = QPushButton("\u25bc 展开")
        toggle_btn.setCheckable(True)
        toggle_btn.setMinimumHeight(25)
        toggle_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: #1A1A1A;
                background-color: #FFF9E6;
                border: 1px solid #D4C080;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QPushButton:checked {
                background-color: #FFE082;
            }
        """)
        toggle_btn.clicked.connect(lambda checked, c=card: self._toggle_details(checked, c))
        date_header.addWidget(toggle_btn)

        layout.addLayout(date_header)

        # ===== 第二行：预览色块（纯展示，不可点击） =====
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(5)

        for entry in entries[:3]:
            color = get_mood_color(entry["score"])
            preview_item = QLabel(f'{entry["emoji"]} {entry["score"]}分')
            preview_item.setStyleSheet(f"""
                font-size: 12px;
                color: #1A1A1A;
                background-color: {color};
                padding: 3px 8px;
                border-radius: 4px;
            """)
            preview_layout.addWidget(preview_item)

        if len(entries) > 3:
            more_label = QLabel(f"+{len(entries) - 3}条更多")
            more_label.setStyleSheet("font-size: 11px; color: #666666; background-color: transparent; padding: 3px 8px; border-radius: 4px; border: 1px solid #D4C080;")
            preview_layout.addWidget(more_label)

        preview_layout.addStretch()
        layout.addLayout(preview_layout)

        # ===== 第三行：详细记录（默认隐藏，点击展开按钮显示） =====
        details_frame = QFrame()
        details_frame.setObjectName('details_frame')
        details_frame.setVisible(False)
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF9E6;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(5)

        for entry in entries:
            time_info = entry.get("time_slot", "总体")
            if time_info == "None" or time_info is None:
                time_info = "总体"

            note_info = f' - {entry["note"]}' if entry.get("note") else ""

            detail_item = QLabel(f"  {time_info}: {entry['emoji']} {entry['mood_label']} ({entry['score']}分){note_info}")
            detail_item.setStyleSheet("font-size: 12px; color: #1A1A1A; padding: 2px 5px;")
            details_layout.addWidget(detail_item)

        layout.addWidget(details_frame)

        return card

    def _toggle_details(self, checked, card):
        """展开/收起指定卡片的详细信息"""
        details_frame = card.findChild(QFrame, "details_frame")
        if details_frame:
            details_frame.setVisible(checked)
        """展开/收起详细信息"""
        # 在 card 中找到 details_frame（它是最后一个子 widget）
        details_frame = None
        for child in card.findChildren(QFrame):
            if child.objectName() == 'details_frame':
                details_frame = child
                break
        if details_frame:
            details_frame.setVisible(checked)

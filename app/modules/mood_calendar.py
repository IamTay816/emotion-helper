from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QMessageBox, QCalendarWidget, QDialog, QApplication, QTextEdit)
from PyQt6.QtCore import Qt, QDate, QLocale
from PyQt6.QtGui import QFont, QPalette, QColor
from datetime import datetime
from app.services.db_service import db_service
from app.utils.helpers import get_mood_color, format_date_for_display


def create_light_palette():
    """创建一个浅色的 QPalette"""
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


class MoodCalendarModule(QWidget):
    """心情日历模块"""

    def __init__(self):
        super().__init__()
        self.current_date = datetime.now()
        self.init_ui()

    def init_ui(self):
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")
            app.setPalette(create_light_palette())
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title_label = QLabel("\U0001f4c5 心情日历")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A1A1A;")
        layout.addWidget(title_label)

        # 月份导航
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("\u25c0 上个月")
        self.prev_btn.setMinimumHeight(35)
        self.prev_btn.setStyleSheet(self._get_nav_button_style())
        self.prev_btn.clicked.connect(self._prev_month)
        nav_layout.addWidget(self.prev_btn)

        self.month_label = QLabel()
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A1A1A;")
        nav_layout.addWidget(self.month_label)

        self.next_btn = QPushButton("下个月 \u25b6")
        self.next_btn.setMinimumHeight(35)
        self.next_btn.setStyleSheet(self._get_nav_button_style())
        self.next_btn.clicked.connect(self._next_month)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # 日历容器（淡黄色背景）
        self.calendar_container = QWidget()
        self.calendar_container.setStyleSheet("""
            QWidget {
                background-color: #FFF9E6;
                border: 2px solid #D4C080;
                border-radius: 10px;
            }
        """)
        cal_layout = QVBoxLayout(self.calendar_container)
        cal_layout.setContentsMargins(5, 5, 5, 5)
        cal_layout.setSpacing(0)

        # 日历组件
        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale(QLocale.Language.Chinese, QLocale.Country.China))
        self.calendar.setGridVisible(True)
        self.calendar.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        self.calendar.setMinimumDate(QDate(2020, 1, 1))
        self.calendar.setMaximumDate(QDate(2030, 12, 31))
        self.calendar.clicked.connect(self._on_date_selected)

        self.calendar.setPalette(create_light_palette())

        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #FFF9E6;
                border: none;
                selection-background-color: #FFE082;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #FFF9E6;
            }
            QCalendarWidget QToolButton {
                color: #1A1A1A;
                background-color: #FFF9E6;
                border: none;
                padding: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #FFE082;
            }
            QCalendarWidget QMenu {
                color: #1A1A1A;
                background-color: #FFF9E6;
            }
            QCalendarWidget QSpinBox QComboBox {
                color: #1A1A1A;
                background-color: #FFF9E6;
            }
            QCalendarWidget QSpinBox QComboBox QAbstractItemView {
                color: #1A1A1A;
                background-color: #FFF9E6;
                selection-background-color: #FFE082;
                selection-color: #1A1A1A;
            }
            QCalendarWidget QAbstractItemView {
                color: #1A1A1A;
                background-color: #FFF9E6;
                selection-background-color: #FFE082;
                selection-color: #1A1A1A;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #CCCCCC;
            }
        """)

        cal_layout.addWidget(self.calendar)
        layout.addWidget(self.calendar_container)

        # 图例
        legend_layout = QHBoxLayout()
        legend_label = QLabel("\u2754\ufe0f 图例：")
        legend_label.setStyleSheet("font-size: 13px; color: #1A1A1A;")
        legend_layout.addWidget(legend_label)

        legends = [
            ("\U0001f62b 1-2分", "#FF6B6B"),
            ("\U0001f614 3-4分", "#FFA07A"),
            ("\U0001f610 5-6分", "#FFD93D"),
            ("\U0001f642 7-8分", "#6BCB77"),
            ("\U0001f60a 9-10分", "#4D96FF"),
        ]

        for text, color in legends:
            legend_item = QLabel(text)
            legend_item.setStyleSheet(
                f"font-size: 12px; color: #1A1A1A; padding: 4px 8px; "
                f"background-color: {color}; border-radius: 4px;"
            )
            legend_layout.addWidget(legend_item)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        # 信息提示
        self.info_label = QLabel("\U0001f4a1 点击日期查看当日心情详情")
        self.info_label.setStyleSheet(
            "font-size: 12px; color: #666666; font-style: italic;"
        )
        layout.addWidget(self.info_label)

        layout.addStretch()
        self.setLayout(layout)

        self._update_month_label()

    def _get_nav_button_style(self):
        return """
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                color: #1A1A1A;
                background-color: #FFFFFF;
                border: 2px solid #D4C080;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #FFF9E6;
                border-color: #F0C419;
            }
        """

    def _prev_month(self):
        year = self.current_date.year
        month = self.current_date.month
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        self.current_date = datetime(year, month, 1)
        self.calendar.setSelectedDate(QDate(year, month, 1))
        self._update_month_label()

    def _next_month(self):
        year = self.current_date.year
        month = self.current_date.month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        self.current_date = datetime(year, month, 1)
        self.calendar.setSelectedDate(QDate(year, month, 1))
        self._update_month_label()

    def _update_month_label(self):
        year = self.current_date.year
        month = self.current_date.month
        self.month_label.setText(f"{year}年{month}月")

    def _on_date_selected(self, date):
        year = date.year()
        month = date.month()
        day = date.day()
        date_str = f"{year}-{month:02d}-{day:02d}"

        entries = db_service.get_daily_mood_entries(date_str)

        if not entries:
            QMessageBox.information(
                self, "\u63d0\u793a", f"{date_str}\n\n当天没有心情记录哦~"
            )
            return

        self._show_day_detail(date_str, entries)

    def _show_day_detail(self, date_str, entries):
        """用 QTextEdit 富文本显示详情，避免 QLabel 样式被覆盖"""
        from collections import Counter

        scores = [e["score"] for e in entries]
        avg_score = sum(scores) / len(scores)

        emojis = [e["emoji"] for e in entries]
        dominant_emoji = Counter(emojis).most_common(1)[0][0]

        summary = db_service.get_daily_summary(date_str)

        # 构建 HTML 内容
        html = f"""
        <div style="font-family: 'Microsoft YaHei', sans-serif; color: #000000; background-color: #FFFFFF;">
            <h2 style="color: #1A1A1A;">\U0001f4c5 {format_date_for_display(date_str)}</h2>
            <p><b>平均评分：</b>{avg_score:.1f}分 &nbsp;&nbsp;
               <b>主导表情：</b>{dominant_emoji} &nbsp;&nbsp;
               <b>记录数：</b>{len(entries)}条</p>
            <hr style="border: 1px solid #D4C080;">
            <p><b>\U0001f4dd 详细记录：</b></p>
        """

        for entry in entries:
            time_info = entry.get("time_slot", "\u603b\u4f53")
            if time_info == "None":
                time_info = "\u603b\u4f53"
            note_suffix = f' - {entry["note"]}' if entry.get("note") else ""
            html += f'<p style="margin-left: 10px; color: #000000;">{time_info} {entry["emoji"]} {entry["mood_label"]} ({entry["score"]}\u5206){note_suffix}</p>'

        if summary and summary.get("summary_text"):
            html += f"""
            <hr style="border: 1px solid #D4C080;">
            <p><b>\U0001f916 AI情绪总结：</b></p>
            <div style="background-color: #FFF9E6; padding: 8px; border-radius: 6px; margin-top: 4px;">
                <p style="color: #1A1A1A;">{summary["summary_text"]}</p>
            </div>
            """

        html += "</div>"

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"\u5fc3\u60c5\u8be6\u60c5 - {date_str}")
        dialog.setMinimumSize(450, 350)
        dialog.setStyleSheet("QDialog { background-color: #FFFFFF; }")

        layout = QVBoxLayout(dialog)

        # 用 QTextEdit 显示 HTML 内容
        text_edit = QTextEdit()
        text_edit.setHtml(html)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                color: #000000 !important;
                background-color: #FFFFFF !important;
                border: 1px solid #D4C080;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(text_edit)

        # 关闭按钮
        close_btn = QPushButton("\u5173\u95ed")
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet(
            "QPushButton { font-size: 14px; font-weight: bold; color: #FFFFFF; background-color: #2196F3; border: none; border-radius: 6px; padding: 6px 12px; } "
            "QPushButton:hover { background-color: #1976D2; }"
        )
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

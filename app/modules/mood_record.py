from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QGroupBox, QComboBox, QButtonGroup, QDialog, QApplication, QScrollArea, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from datetime import datetime
from app.services.db_service import db_service
from app.services.mood_analyzer import MoodAnalyzer
from app.models.mood_entry import MoodEntry, MoodLevel
from app.utils.helpers import get_current_date, get_current_time, get_mood_options, get_mood_color


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


class SummaryDialog(QDialog):
    """总结展示对话框"""
    
    def __init__(self, summary_data, parent=None):
        super().__init__(parent)
        self.summary_data = summary_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("\U0001f916 AI 情绪总结")
        self.setMinimumSize(500, 400)
        self.setPalette(create_light_palette())
        self.setStyleSheet("QDialog { background-color: #FFFFFF; }")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title = QLabel(f"\U0001f4c5 {self.summary_data['date']} AI 情绪总结")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A1A1A;")
        layout.addWidget(title)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        avg_label = QLabel(f"\u5e73\u5747\u5206\uff1a{self.summary_data['avg_score']:.1f}分")
        avg_label.setStyleSheet("font-size: 13px; color: #1A1A1A;")
        stats_layout.addWidget(avg_label)
        
        emoji_label = QLabel(f"\u4e3b\u5bfc\u8868\u60c5\uff1a{self.summary_data['dominant_emoji']}")
        emoji_label.setStyleSheet("font-size: 13px; color: #1A1A1A;")
        stats_layout.addWidget(emoji_label)
        
        count_label = QLabel(f"\u8bb0\u5f55\u6570\uff1a{self.summary_data['total_records']}条")
        count_label.setStyleSheet("font-size: 13px; color: #1A1A1A;")
        stats_layout.addWidget(count_label)
        
        layout.addLayout(stats_layout)
        
        # 分隔线
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #D4C080;")
        layout.addWidget(separator)
        
        # 总结内容（用 QTextEdit 避免样式覆盖问题）
        from PyQt6.QtWidgets import QTextEdit
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(self._format_summary_html())
        text_edit.setStyleSheet("""
            QTextEdit {
                color: #1A1A1A !important;
                background-color: #FFF9E6 !important;
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
        close_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #2196F3;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _format_summary_html(self):
        """将总结文本格式化为 HTML"""
        text = self.summary_data.get('summary_text', '暂无总结内容')
        # 将换行符转换为 <br>
        html = text.replace('\n', '<br>')
        return f'<div style="font-size: 13px; color: #1A1A1A; line-height: 1.6;">{html}</div>'


class MoodRecordModule(QWidget):
    mood_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_date = get_current_date()
        self.slot_enabled = True
        self.analyzer = MoodAnalyzer()
        self.init_ui()
        self.load_today_moods()
        
        # 初始化后设置时段默认值
        self._on_slot_score_selected(10)
        self._update_emoji_buttons(self.slot_emoji_buttons, 10)
        
        # 初始化时段按钮状态为"开启"
        self.slot_enabled = True
        self.slot_combo.setVisible(True)
        self.slot_score_label.setVisible(True)
        self.slot_slider.setVisible(True)
        self.slot_emoji_label.setVisible(True)
        for btn in self.slot_emoji_buttons:
            btn.setVisible(True)
        self.slot_note_label.setVisible(True)
        self.slot_note.setVisible(True)
        self.slot_toggle_btn.setText('关闭时段记录')
        self.slot_toggle_btn.setStyleSheet('font-size: 13px; font-weight: bold; color: #FFFFFF; background-color: #4CAF50; border: none; border-radius: 6px; padding: 6px 12px;')
        self.slot_toggle_btn.setChecked(True)
    
    def init_ui(self):
        # 使用滚动区域包裹所有内容
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #FFFFFF; }")
        
        scroll_content = QWidget()
        layout_main = QVBoxLayout(scroll_content)
        layout_main.setSpacing(15)
        layout_main.setContentsMargins(15, 15, 15, 15)
        
        # 强制使用浅色风格
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")
            app.setPalette(create_light_palette())
        
        # 标题行（日期 + 生成总结按钮）
        header_layout = QHBoxLayout()
        
        date_label = QLabel(f'今日日期：{self.current_date}')
        date_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #1A1A1A;')
        header_layout.addWidget(date_label)
        
        header_layout.addStretch()
        
        # 生成总结按钮
        summary_btn = QPushButton('\U0001f916 生成今日总结')
        summary_btn.setMinimumHeight(30)
        summary_btn.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #FF9800;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        ''')
        summary_btn.clicked.connect(self._show_summary_dialog)
        header_layout.addWidget(summary_btn)
        
        layout_main.addLayout(header_layout)
        
        daily_group = self._create_daily_mood_group()
        layout_main.addWidget(daily_group)
        
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet('background-color: #D4C080;')
        layout_main.addWidget(separator)
        
        slot_group = self._create_slot_mood_group()
        layout_main.addWidget(slot_group)
        
        save_btn = QPushButton('保存今日记录')
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet('background-color: #4CAF50; color: #FFFFFF; border: none; border-radius: 8px; padding: 8px; font-size: 14px; font-weight: bold;')
        save_btn.clicked.connect(self.save_mood_entries)
        layout_main.addWidget(save_btn)
        

        export_btn = QPushButton('导出数据')
        export_btn.setMinimumHeight(40)
        export_btn.setStyleSheet('background-color: #2196F3; color: #FFFFFF; border: none; border-radius: 8px; padding: 8px; font-size: 14px; font-weight: bold;')
        export_btn.clicked.connect(self.export_data)
        layout_main.addWidget(export_btn)
        tip_label = QLabel('提示：总体心情和时段心情都是可选的，想记录就记录，不记录也没关系～')
        tip_label.setStyleSheet('font-size: 12px; color: #666666; font-style: italic;')
        tip_label.setWordWrap(True)
        layout_main.addWidget(tip_label)
        
        layout_main.addStretch()
        
        # 将滚动内容放入滚动区域
        scroll.setWidget(scroll_content)
        
        # 将滚动区域加入主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    def _show_summary_dialog(self):
        """显示今日情绪总结"""
        # 先分析生成总结
        result = self.analyzer.analyze_daily_mood(self.current_date)
        
        if not result:
            QMessageBox.warning(
                self,
                "\u63d0\u793a",
                f"{self.current_date}\n\n当天还没有心情记录哦～\n\n先去记录心情后再查看总结吧！"
            )
            return
        
        # 显示总结对话框
        dialog = SummaryDialog(result, self)
        dialog.exec()
    
    def _create_daily_mood_group(self):
        group = QGroupBox('今日总体心情')
        group.setStyleSheet('font-size: 14px; font-weight: bold; color: #1A1A1A; border: 2px solid #D4C080; border-radius: 10px; padding-top: 12px;')
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # --- 滑动条 + 表情联动（水平排列，与时段一致） ---
        slider_layout = QHBoxLayout()
        
        self.daily_score_label = QLabel('评分：')
        self.daily_score_label.setStyleSheet('font-size: 13px; font-weight: bold; color: #1A1A1A;')
        slider_layout.addWidget(self.daily_score_label)
        
        self.daily_slider = QSlider(Qt.Orientation.Horizontal)
        self.daily_slider.setMinimum(1)
        self.daily_slider.setMaximum(10)
        self.daily_slider.setValue(0)
        self.daily_slider.setFixedWidth(300)
        self.daily_slider.setMinimumHeight(30)
        self.daily_slider.setStyleSheet('''
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #EFE8D0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FF6B35;
                border: 2px solid #333333;
                border-radius: 4px;
                width: 20px;
                margin: -4px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #E55520;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, x2:1, stop:0 #FF6B6B, stop:0.2 #FFA07A, stop:0.4 #FFD93D, stop:0.6 #B8E6B2, stop:0.8 #6BCB77, stop:1 #4D96FF);
                border-radius: 4px;
            }
        ''')
        self.daily_slider.valueChanged.connect(self._on_slider_value_changed)
        # 隐藏的评分按钮组（供表情联动和保存使用）
        self.score_radios = []
        self.daily_score_group = QButtonGroup()
        for i in range(1, 11):
            radio = QPushButton(str(i))
            radio.setCheckable(True)
            radio.setVisible(False)  # 隐藏不显示
            radio.clicked.connect(lambda checked, num=i: self._on_score_selected(num))
            self.daily_score_group.addButton(radio)
            self.score_radios.append(radio)
        slider_layout.addWidget(self.daily_slider)
        
        self.slider_score_display = QLabel('未选择')
        self.slider_score_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_score_display.setStyleSheet('font-size: 14px; font-weight: bold; color: #1A1A1A; min-height: 22px;')
        slider_layout.addWidget(self.slider_score_display)
        slider_layout.addStretch()
        layout.addLayout(slider_layout)
        
        # --- 表情行 ---
        emoji_layout = QHBoxLayout()
        emoji_label = QLabel('表情：')
        emoji_label.setStyleSheet('font-size: 13px; font-weight: bold; color: #1A1A1A;')
        emoji_layout.addWidget(emoji_label)
        
        self.daily_emoji_group = QButtonGroup()
        self.emoji_buttons = []
        emojis = [('😫', 1), ('😔', 3), ('😐', 5), ('🙂', 7), ('😊', 9)]
        
        for emoji_text, score in emojis:
            btn = QPushButton(emoji_text)
            btn.setCheckable(True)
            btn.setFixedSize(50, 35)
            btn.setStyleSheet(self._get_emoji_button_style(score))
            btn.clicked.connect(lambda checked, s=score: self._on_emoji_selected(s))
            self.daily_emoji_group.addButton(btn)
            emoji_layout.addWidget(btn)
            self.emoji_buttons.append(btn)
        
        emoji_layout.addStretch()
        layout.addLayout(emoji_layout)
        
        # --- 备注 ---
        note_layout = QHBoxLayout()
        note_label = QLabel('备注：')
        note_label.setStyleSheet('font-size: 13px; font-weight: bold; color: #1A1A1A;')
        note_layout.addWidget(note_label)
        
        self.daily_note = QTextEdit()
        self.daily_note.setMaximumHeight(60)
        self.daily_note.setStyleSheet('''
            QTextEdit {
                font-size: 13px;
                color: #1A1A1A;
                background-color: #FFFFFF;
                border: 2px solid #D4C080;
                border-radius: 6px;
                padding: 6px;
            }
        ''')
        note_layout.addWidget(self.daily_note)
        
        layout.addLayout(note_layout)
        group.setLayout(layout)
        return group
    def _on_slider_value_changed(self, value):
        """滑动条值改变时，同步更新表情和显示"""
        if value == 0:
            self.slider_score_display.setText('未选择')
            self.slider_score_display.setStyleSheet('font-size: 16px; font-weight: bold; color: #1A1A1A; min-height: 25px;')
            return
        
        self.slider_score_display.setText(f'当前评分：{value} 分')
        
        # 确定表情索引
        if value <= 2:
            target = 0
        elif value <= 4:
            target = 1
        elif value <= 6:
            target = 2
        elif value <= 8:
            target = 3
        else:
            target = 4
        
        self._update_emoji_buttons(self.emoji_buttons, value)
        
        # 同时更新隐藏的日常评分按钮组状态
        for i, radio in enumerate(self.score_radios, 1):
            if i == value:
                radio.setStyleSheet(self._get_score_button_checked_style(i))
                radio.setChecked(True)
            else:
                radio.setStyleSheet(self._get_score_button_style(i))
                radio.setChecked(False)

    def _create_slot_mood_group(self):
        group = QGroupBox('时段心情记录（可选）')
        group.setStyleSheet('font-size: 13px; font-weight: bold; color: #1A1A1A; border: 2px solid #D4C080; border-radius: 10px; padding-top: 12px;')
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 时段选择行
        slot_top_layout = QHBoxLayout()
        
        time_label = QLabel('时间段：')
        time_label.setStyleSheet('font-size: 13px; color: #1A1A1A;')
        slot_top_layout.addWidget(time_label)
        
        self.slot_combo = QComboBox()
        self.slot_combo.setMinimumHeight(30)
        self.slot_combo.setStyleSheet('''
            QComboBox {
                font-size: 12px;
                color: #1A1A1A;
                background-color: #FFFFFF;
                border: 1px solid #D4C080;
                border-radius: 4px;
                padding: 3px;
            }
            QComboBox QAbstractItemView {
                color: #1A1A1A;
                background-color: #FFFFFF;
                selection-background-color: #FFE082;
            }
        ''')
        for hour in range(24):
            self.slot_combo.addItem(f'{hour:02d}:00')
        slot_top_layout.addWidget(self.slot_combo)
        
        self.slot_toggle_btn = QPushButton('开启时段记录')
        self.slot_toggle_btn.setMinimumHeight(30)
        self.slot_toggle_btn.setCheckable(True)
        self.slot_toggle_btn.setStyleSheet('''
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #4CAF50;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:checked {
                background-color: #F44336;
            }
        ''')
        self.slot_toggle_btn.clicked.connect(self._toggle_slots)
        slot_top_layout.addWidget(self.slot_toggle_btn)
        
        slot_top_layout.addStretch()
        layout.addLayout(slot_top_layout)
        
        # 时段评分滑动条
        slot_slider_layout = QHBoxLayout()
        self.slot_score_label = QLabel('评分：')
        self.slot_score_label.setStyleSheet('font-size: 13px; font-weight: bold; color: #1A1A1A;')
        slot_slider_layout.addWidget(self.slot_score_label)

        self.slot_slider = QSlider(Qt.Orientation.Horizontal)
        self.slot_slider.setMinimum(1)
        self.slot_slider.setMaximum(10)
        self.slot_slider.setValue(0)
        self.slot_slider.setFixedWidth(300)
        self.slot_slider.setMinimumHeight(30)
        self.slot_slider.setStyleSheet('''
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #EFE8D0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FF6B35;
                border: 2px solid #333333;
                border-radius: 4px;
                width: 20px;
                margin: -4px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #E55520;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, x2:1, stop:0 #FF6B6B, stop:0.2 #FFA07A, stop:0.4 #FFD93D, stop:0.6 #B8E6B2, stop:0.8 #6BCB77, stop:1 #4D96FF);
                border-radius: 4px;
            }
        ''')
        self.slot_slider.valueChanged.connect(self._on_slot_slider_value_changed)
        slot_slider_layout.addWidget(self.slot_slider)

        self.slot_slider_display = QLabel('未选择')
        self.slot_slider_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slot_slider_display.setStyleSheet('font-size: 14px; font-weight: bold; color: #1A1A1A; min-height: 22px;')
        slot_slider_layout.addWidget(self.slot_slider_display)
        slot_slider_layout.addStretch()
        layout.addLayout(slot_slider_layout)
        
        # 时段表情行
        slot_emoji_layout = QHBoxLayout()
        self.slot_emoji_label = QLabel('表情：')
        self.slot_emoji_label.setStyleSheet('font-size: 13px; color: #1A1A1A;')
        slot_emoji_layout.addWidget(self.slot_emoji_label)
        
        self.slot_emoji_group = QButtonGroup()
        self.slot_emoji_buttons = []
        emojis = [('😫', 1), ('😔', 3), ('😐', 5), ('🙂', 7), ('😊', 9)]
        
        for emoji_text, score in emojis:
            btn = QPushButton(emoji_text)
            btn.setCheckable(True)
            btn.setFixedSize(50, 35)
            btn.setStyleSheet(self._get_emoji_button_style(score))
            btn.clicked.connect(lambda checked, s=score: self._on_slot_emoji_selected(s))
            self.slot_emoji_group.addButton(btn)
            slot_emoji_layout.addWidget(btn)
            self.slot_emoji_buttons.append(btn)
        
        slot_emoji_layout.addStretch()
        layout.addLayout(slot_emoji_layout)
        
        # 时段备注
        slot_note_layout = QHBoxLayout()
        self.slot_note_label = QLabel('备注：')
        self.slot_note_label.setStyleSheet('font-size: 13px; color: #1A1A1A;')
        slot_note_layout.addWidget(self.slot_note_label)
        
        self.slot_note = QTextEdit()
        self.slot_note.setMaximumHeight(60)
        self.slot_note.setStyleSheet('''
            QTextEdit {
                font-size: 12px;
                color: #1A1A1A;
                background-color: #FFFFFF;
                border: 1px solid #D4C080;
                border-radius: 4px;
                padding: 4px;
            }
        ''')
        slot_note_layout.addWidget(self.slot_note)
        
        layout.addLayout(slot_note_layout)
        
        # 初始隐藏时段控件

        for btn in self.slot_emoji_buttons:
            btn.setVisible(False)
        self.slot_note.setVisible(False)
        self.slot_combo.setVisible(True)
        self.slot_score_label.setVisible(False)
        self.slot_slider.setVisible(True)
        self.slot_slider_display.setVisible(True)
        self.slot_emoji_label.setVisible(False)
        self.slot_note_label.setVisible(False)
        
        group.setLayout(layout)
        return group
    
    def _toggle_slots(self, checked):
        """切换时段记录的显示/隐藏"""
        self.slot_enabled = checked
        
        self.slot_slider.setVisible(checked)
        self.slot_slider_display.setVisible(checked)
        for btn in self.slot_emoji_buttons:
            btn.setVisible(checked)
        self.slot_note.setVisible(checked)
        self.slot_combo.setVisible(checked)
        self.slot_score_label.setVisible(checked)
        self.slot_emoji_label.setVisible(checked)
        self.slot_note_label.setVisible(checked)
        
        if checked:
            self.slot_toggle_btn.setText('关闭时段记录')
            self.slot_toggle_btn.setStyleSheet('font-size: 13px; font-weight: bold; color: #FFFFFF; background-color: #4CAF50; border: none; border-radius: 6px; padding: 6px 12px;')
        else:
            self.slot_toggle_btn.setText('开启时段记录')
            self.slot_toggle_btn.setStyleSheet('font-size: 13px; font-weight: bold; color: #FFFFFF; background-color: #F44336; border: none; border-radius: 6px; padding: 6px 12px;')
    
    def _get_score_button_style(self, score):
        color = get_mood_color(score)
        return f'''
            QPushButton {{
                font-size: 12px;
                font-weight: bold;
                color: #1A1A1A;
                background-color: {color};
                border: 2px solid #BBBBBB;
                border-radius: 4px;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
                border-color: #999999;
            }}
        '''
    
    def _get_score_button_checked_style(self, score):
        color = get_mood_color(score)
        return f'''
            QPushButton {{
                font-size: 12px;
                font-weight: bold;
                color: #1A1A1A;
                background-color: {color};
                border: 3px solid #000000;
                border-radius: 4px;
                padding: 2px;
            }}
        '''
    
    def _get_emoji_button_style(self, score):
        # 表情使用固定颜色，根据评分范围映射
        if score <= 2:
            color = "#FF6B6B"
        elif score <= 4:
            color = "#FFA07A"
        elif score <= 6:
            color = "#FFD93D"
        elif score <= 8:
            color = "#6BCB77"
        else:
            color = "#4D96FF"
        return f'''
            QPushButton {{
                font-size: 18px;
                background-color: {color};
                border: 2px solid #BBBBBB;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
                border-color: #999999;
            }}
        '''
    
    def _get_emoji_button_checked_style(self, score):
        # 表情使用固定颜色，根据评分范围映射
        if score <= 2:
            color = "#FF6B6B"
        elif score <= 4:
            color = "#FFA07A"
        elif score <= 6:
            color = "#FFD93D"
        elif score <= 8:
            color = "#6BCB77"
        else:
            color = "#4D96FF"
        return f'''
            QPushButton {{
                font-size: 18px;
                background-color: {color};
                border: 3px solid #000000;
                border-radius: 6px;
            }}
        '''
    
    def _on_score_selected(self, score):
        # 同步更新滑动条
        self.daily_slider.setValue(score)
        self.slider_score_display.setText(f'当前评分：{score} 分')
        for i, radio in enumerate(self.score_radios, 1):
            if i == score:
                radio.setStyleSheet(self._get_score_button_checked_style(i))
                radio.setChecked(True)
            else:
                radio.setStyleSheet(self._get_score_button_style(i))
                radio.setChecked(False)
        
        self._update_emoji_buttons(self.emoji_buttons, score)
    
    def _on_emoji_selected(self, score):
        self._on_score_selected(score)
    
    def _update_emoji_buttons(self, buttons, score):
        # 根据评分确定选中的表情索引
        if score <= 2:
            target = 0
        elif score <= 4:
            target = 1
        elif score <= 6:
            target = 2
        elif score <= 8:
            target = 3
        else:
            target = 4

        # 每个表情有固定颜色，不随评分变化
        emoji_fixed_colors = ["#FF6B6B", "#FFA07A", "#FFD93D", "#6BCB77", "#4D96FF"]

        for i, btn in enumerate(buttons):
            if i == target:
                color = emoji_fixed_colors[i]
                btn.setStyleSheet(f"""
                    QPushButton {{
                        font-size: 18px;
                        background-color: {color};
                        border: 3px solid #000000;
                        border-radius: 6px;
                    }}
                """)
                btn.setChecked(True)
            else:
                color = emoji_fixed_colors[i]
                btn.setStyleSheet(f"""
                    QPushButton {{
                        font-size: 18px;
                        background-color: {color};
                        border: 2px solid #BBBBBB;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {color}dd;
                        border-color: #999999;
                    }}
                """)
                btn.setChecked(False)
    def _on_slot_slider_value_changed(self, value):
        """滑动条值改变时，同步更新时段表情"""
        if value == 0:
            self.slot_slider_display.setText('未选择')
            return
        self.slot_slider_display.setText(f'当前评分：{value} 分')
        self._update_emoji_buttons(self.slot_emoji_buttons, value)
        if value == 0:
            return
        self._update_emoji_buttons(self.slot_emoji_buttons, value)

    def _on_slot_score_selected(self, score):
        # 同步更新滑动条
        self.slot_slider.setValue(score)
        self._update_emoji_buttons(self.slot_emoji_buttons, score)
        self.slot_slider_display.setText(f'当前评分：{score} 分')
    def _on_slot_emoji_selected(self, score):
        self._on_slot_score_selected(score)
    
    def load_today_moods(self):
        entries = db_service.get_daily_mood_entries(self.current_date)
        
        if not entries:
            return
        
        daily_entries = [e for e in entries if e['record_type'] == 'daily']
        if daily_entries:
            entry = daily_entries[0]
            self._on_score_selected(entry['score'])
            self.daily_note.setPlainText(entry.get('note', ''))
        
        slot_entries = [e for e in entries if e['record_type'] == 'slot']
        if slot_entries:
            entry = slot_entries[-1]
            idx = int(entry['time_slot'].split(':')[0])
            self.slot_combo.setCurrentIndex(idx)
            self._on_slot_score_selected(entry['score'])
            self.slot_note.setPlainText(entry.get('note', ''))
    
    def _auto_backup(self):
        """自动备份数据库到 data/backups/ 文件夹"""
        import shutil
        import os
        from datetime import datetime
        
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "emoodie_db.sqlite")
        if os.path.exists(db_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"emoodie_backup_{timestamp}.sqlite")
            shutil.copy2(db_path, backup_file)
            
            # 只保留最近7天的备份
            backup_files = sorted(os.listdir(backup_dir))
            while len(backup_files) > 7:
                os.remove(os.path.join(backup_dir, backup_files.pop(0)))

    def export_data(self):
        """导出数据为 JSON 文件"""
        from PyQt6.QtWidgets import QFileDialog
        import json
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "", "JSON 文件 (*.json)"
        )
        
        if not file_path:
            return
        
        # 读取所有心情记录
        from app.services.db_service import db_service
        entries = db_service.get_all_mood_entries(limit=10000)
        
        data = {
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": len(entries),
            "records": entries
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        QMessageBox.information(
            self, "导出成功", f"已导出 {len(entries)} 条记录到:\n{file_path}"
        )

    def save_mood_entries(self):
        saved_count = 0
        
        selected_score = self.daily_slider.value()
        
        if selected_score:
            mood_level = MoodLevel.get_by_score(selected_score)
            entry = MoodEntry(
                date=self.current_date,
                score=selected_score,
                emoji=mood_level.emoji,
                mood_label=mood_level.label,
                note=self.daily_note.toPlainText(),
                record_type='daily'
            )
            db_service.insert_mood_entry(entry.to_dict())
            saved_count += 1
        
        if self.slot_enabled:
            slot_score = self.slot_slider.value()
            
            if slot_score:
                mood_level = MoodLevel.get_by_score(slot_score)
                time_slot = self.slot_combo.currentText()
                entry = MoodEntry(
                    date=self.current_date,
                    time_slot=time_slot,
                    score=slot_score,
                    emoji=mood_level.emoji,
                    mood_label=mood_level.label,
                    note=self.slot_note.toPlainText(),
                    record_type='slot'
                )
                db_service.insert_mood_entry(entry.to_dict())
                saved_count += 1
        
        if saved_count > 0:
            self._auto_backup()
            self._show_success_dialog(saved_count)
            self.mood_saved.emit()
        else:
            self._show_warning_dialog()
    
    def _show_success_dialog(self, count):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle('保存成功')
        msg.setText(f'成功保存 {count} 条记录！')
        msg.setInformativeText('继续加油～')
        
        ok_button = msg.button(QMessageBox.StandardButton.Ok)
        if ok_button:
            ok_button.setStyleSheet('background-color: #4CAF50 !important; color: #FFFFFF !important; border: none !important; border-radius: 5px; padding: 8px 20px; font-size: 14px; font-weight: bold;')
        
        msg.setStyleSheet('''
            QMessageBox {
                background-color: #FFFFFF !important;
            }
            QMessageBox QLabel {
                color: #1A1A1A !important;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50 !important;
                color: #FFFFFF !important;
            }
        ''')
        msg.exec()
    
    def _show_warning_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle('提示')
        msg.setText('没有选择任何心情记录哦～')
        msg.setInformativeText('想记录的话就选一个吧！')
        
        ok_button = msg.button(QMessageBox.StandardButton.Ok)
        if ok_button:
            ok_button.setStyleSheet('background-color: #2196F3 !important; color: #FFFFFF !important; border: none !important; border-radius: 5px; padding: 8px 20px; font-size: 14px; font-weight: bold;')
        
        msg.setStyleSheet('''
            QMessageBox {
                background-color: #FFFFFF !important;
            }
            QMessageBox QLabel {
                color: #1A1A1A !important;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #2196F3 !important;
                color: #FFFFFF !important;
            }
        ''')
        msg.exec()

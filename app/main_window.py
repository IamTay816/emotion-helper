import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.modules.mood_record import MoodRecordModule
from app.modules.mood_calendar import MoodCalendarModule
from app.modules.history_view import HistoryViewModule
from app.modules.chat_helper import ChatHelperModule


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('情绪疏导小助手')
        self.setGeometry(100, 100, 1000, 750)
        
        # 加载样式
        self.load_stylesheet()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel('情绪疏导小助手')
        title_label.setStyleSheet('font-size: 26px; font-weight: bold; color: #1A1A1A;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 导航按钮容器
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setSpacing(15)
        
        self.btn_mood = QPushButton('📝 心情记录')
        self.btn_calendar = QPushButton('📅 心情日历')
        self.btn_history = QPushButton('📖 历史记录')
        self.btn_chat = QPushButton('💬 对话助手')
        
        for btn in [self.btn_mood, self.btn_calendar, self.btn_history, self.btn_chat]:
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_layout.addWidget(btn)
        
        self._setup_nav_buttons()
        
        # 添加导航容器到主布局
        main_layout.addWidget(nav_container)
        
        # 分隔线
        separator = QLabel()
        separator.setFixedHeight(2)
        separator.setStyleSheet('background-color: #E8D5A3;')
        main_layout.addWidget(separator)
        
        # 内容区域（使用堆叠widget）
        self.stack = QStackedWidget()
        self.stack.setStyleSheet('background-color: #FFFFFF; border-radius: 12px;')
        main_layout.addWidget(self.stack)
        
        # 创建各个模块
        self.mood_module = MoodRecordModule()
        self.calendar_module = MoodCalendarModule()
        self.history_module = HistoryViewModule()
        self.chat_module = ChatHelperModule()
        
        # 添加模块到堆叠widget
        self.stack.addWidget(self.mood_module)
        self.stack.addWidget(self.calendar_module)
        self.stack.addWidget(self.history_module)
        self.stack.addWidget(self.chat_module)
        
        # 连接导航按钮
        self.btn_mood.clicked.connect(lambda: self.switch_page(0))
        self.btn_calendar.clicked.connect(lambda: self.switch_page(1))
        self.btn_history.clicked.connect(lambda: self.switch_page(2))
        self.btn_chat.clicked.connect(lambda: self.switch_page(3))
        
        # 默认选中心情记录
        self.btn_mood.setChecked(True)
    
    def _setup_nav_buttons(self):
        """设置导航按钮样式"""
        base_style = '''
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                color: #1A1A1A;
                border: 2px solid #E8D5A3;
                border-radius: 12px;
                background-color: #FFFDF5;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FFF9E6;
                border-color: #F0C419;
                color: #F0C419;
            }
            QPushButton:checked {
                background-color: #FFF0B3;
                border-color: #F0C419;
                color: #1A1A1A;
                font-weight: bold;
            }
        '''
        for btn in [self.btn_mood, self.btn_calendar, self.btn_history, self.btn_chat]:
            btn.setStyleSheet(base_style)
    
    def load_stylesheet(self):
        """加载样式表"""
        self.setStyleSheet('''
            QMainWindow {
                background-color: #FFF9E6;
            }
        ''')
    
    def switch_page(self, index):
        """切换页面"""
        # 更新按钮状态
        for btn in [self.btn_mood, self.btn_calendar, self.btn_history, self.btn_chat]:
            btn.setChecked(False)
        
        # 选中对应的按钮
        buttons = [self.btn_mood, self.btn_calendar, self.btn_history, self.btn_chat]
        if 0 <= index < len(buttons):
            buttons[index].setChecked(True)
        
        # 切换内容
        self.stack.setCurrentIndex(index)
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        # 清理对话助手中未发言的空会话
        self.chat_module.cleanup_empty_sessions()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont('Microsoft YaHei', 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

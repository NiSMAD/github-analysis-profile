from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QTabWidget, QProgressBar, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt
from github import Github, BadCredentialsException

class TokenDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Token Setup")
        self.setFixedSize(400, 200)
        
        layout = QFormLayout()
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your GitHub personal access token")
        self.token_input.setEchoMode(QLineEdit.Password)
        
        self.info_label = QLabel(
            "<a href='https://github.com/settings/tokens'>How to get token</a>"
            "<br><br>Token needs <b>public_repo</b> scope"
        )
        self.info_label.setOpenExternalLinks(True)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.validate_token)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow("GitHub Token:", self.token_input)
        layout.addRow(self.info_label)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def validate_token(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Error", "Please enter a token!")
            return
            
        try:
            g = Github(token)
            user = g.get_user()
            self.accept()
        except BadCredentialsException:
            QMessageBox.critical(self, "Invalid Token", 
                "The token is invalid!\n"
                "Please check and enter a valid GitHub personal access token.")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Connection error: {str(e)}\n"
                "Please check your internet connection.")

class GitHubAnalyzerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Profile Analyzer Pro")
        self.setFixedSize(1000, 800)
        self.token = None
        
        # Инициализация UI
        self.init_ui()
        
        # Показываем диалог токена
        self.show_token_dialog()

    def init_ui(self):
        """Инициализация всего интерфейса"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Секция ввода
        self.input_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter GitHub username...")
        self.analyze_btn = QPushButton("Analyze")
        
        self.input_layout.addWidget(QLabel("GitHub Username:"))
        self.input_layout.addWidget(self.username_input)
        self.input_layout.addWidget(self.analyze_btn)
        
        # Прогресс-бар
        self.progress = QProgressBar()
        self.progress.hide()
        
        # Вкладки
        self.tabs = QTabWidget()
        self.init_tabs()
        
        # Кнопки управления
        self.controls_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Report")
        self.save_btn.setEnabled(False)
        self.clear_btn = QPushButton("Clear")
        
        self.controls_layout.addWidget(self.save_btn)
        self.controls_layout.addWidget(self.clear_btn)
        
        # Собираем все вместе
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.progress)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addLayout(self.controls_layout)

    def init_tabs(self):
        """Инициализация вкладок"""
        # Вкладка Overview
        self.tab_overview = QWidget()
        self.overview_layout = QVBoxLayout()
        self.overview_label = QLabel("General statistics will appear here")
        self.overview_label.setAlignment(Qt.AlignCenter)
        self.overview_layout.addWidget(self.overview_label)
        self.tab_overview.setLayout(self.overview_layout)
        
        # Вкладка Activity
        self.tab_activity = QWidget()
        self.activity_layout = QVBoxLayout()
        self.activity_label = QLabel("Activity analysis will appear here")
        self.activity_label.setAlignment(Qt.AlignCenter)
        self.activity_layout.addWidget(self.activity_label)
        self.tab_activity.setLayout(self.activity_layout)
        
        self.tabs.addTab(self.tab_overview, "Overview")
        self.tabs.addTab(self.tab_activity, "Activity")

    def show_token_dialog(self):
        """Показываем диалог ввода токена"""
        dialog = TokenDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.token = dialog.token_input.text().strip()
            if not self.token:
                QMessageBox.warning(self, "Warning", 
                    "You didn't enter a token. Some features may be limited.")
        else:
            QMessageBox.warning(self, "Warning", 
                "You can set token later in Settings.")

    def clear_tab(self, tab):
        """Очищаем содержимое вкладки"""
        layout = tab.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

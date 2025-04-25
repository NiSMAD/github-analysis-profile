import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QTabWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from github import Github
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GitHubAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Profile Analyzer Pro")
        self.setFixedSize(1000, 800)
        
        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Макет
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Элементы UI
        self.setup_ui()
        
        # Переменные для хранения данных
        self.current_username = ""
        self.figure = None
        self.canvas = None
    
    def setup_ui(self):
        # Поле ввода
        self.input_layout = QHBoxLayout()
        self.label = QLabel("GitHub Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter GitHub username...")
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.analyze_profile)
        
        self.input_layout.addWidget(self.label)
        self.input_layout.addWidget(self.username_input)
        self.input_layout.addWidget(self.analyze_btn)
        
        # Кнопки действий
        self.buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Report")
        self.save_btn.clicked.connect(self.save_report)
        self.save_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        
        self.buttons_layout.addWidget(self.save_btn)
        self.buttons_layout.addWidget(self.clear_btn)
        
        # Вкладки для результатов
        self.tabs = QTabWidget()
        self.tab_overview = QWidget()
        self.tab_activity = QWidget()
        
        self.tabs.addTab(self.tab_overview, "Overview")
        self.tabs.addTab(self.tab_activity, "Activity")
        
        # Настройка вкладок
        self.setup_tabs()
        
        # Добавляем все в основной макет
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.tabs)
        self.layout.addLayout(self.buttons_layout)
    
    def setup_tabs(self):
        # Вкладка Overview
        self.overview_layout = QVBoxLayout()
        self.overview_label = QLabel("General statistics will appear here")
        self.overview_label.setAlignment(Qt.AlignCenter)
        self.overview_label.setStyleSheet("font-size: 16px;")
        self.overview_layout.addWidget(self.overview_label)
        self.tab_overview.setLayout(self.overview_layout)
        
        # Вкладка Activity
        self.activity_layout = QVBoxLayout()
        self.activity_label = QLabel("Activity analysis will appear here")
        self.activity_label.setAlignment(Qt.AlignCenter)
        self.activity_label.setStyleSheet("font-size: 16px;")
        self.activity_layout.addWidget(self.activity_label)
        self.tab_activity.setLayout(self.activity_layout)
    
    def analyze_profile(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a GitHub username")
            return
        
        try:
            self.current_username = username
            g = Github()
            user = g.get_user(username)
            
            # Собираем основные данные
            languages = []
            repo_topics = []
            repo_dates = []
            
            for repo in user.get_repos():
                if not repo.fork:
                    if repo.language:
                        languages.append(repo.language)
                    repo_topics.extend(repo.get_topics())
                    repo_dates.append(repo.created_at)
            
            # Анализ языков и тегов
            lang_stats = pd.Series(languages).value_counts().head(5)
            topics_stats = pd.Series(repo_topics).value_counts().head(5)
            
            # Анализ активности
            current_year = datetime.now().year
            repo_dates_this_year = [d for d in repo_dates if d.year == current_year]
            
            if repo_dates_this_year:
                activity_df = pd.DataFrame({
                    'date': repo_dates_this_year
                })
                activity_df['date'] = pd.to_datetime(activity_df['date'])
                activity_stats = activity_df.resample('M', on='date').size()
            else:
                activity_stats = pd.Series(dtype=int)
            
            # Показываем результаты
            self.show_overview(lang_stats, topics_stats)
            self.show_activity(activity_stats, current_year)
            
            # Сохраняем данные для возможного сохранения
            self.lang_stats = lang_stats
            self.topics_stats = topics_stats
            self.activity_stats = activity_stats
            self.current_year = current_year
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to analyze profile: {str(e)}")
    
    def show_overview(self, lang_stats, topics_stats):
        # Очищаем предыдущий график
        self.clear_tab(self.tab_overview)
        
        # Создаем новый график
        fig, axes = plt.subplots(1, 2, figsize=(10, 4)) if not topics_stats.empty else plt.subplots(1, 1, figsize=(5, 4))
        
        # График языков
        if topics_stats.empty:
            ax = axes
        else:
            ax = axes[0]
        
        lang_stats.plot(kind='bar', ax=ax, title='Top Languages', color='skyblue')
        ax.set_ylabel('Count')
        
        # График тегов (если есть)
        if not topics_stats.empty:
            topics_stats.plot(kind='bar', ax=axes[1], title='Top Topics', color='lightgreen')
            axes[1].set_ylabel('Count')
        
        fig.tight_layout()
        
        # Встраиваем график в Qt
        canvas = FigureCanvas(fig)
        self.overview_layout.addWidget(canvas)
        
        # Обновляем текст
        self.overview_label.setText(f"General statistics for {self.current_username}")
    
    def show_activity(self, activity_stats, current_year):
        # Очищаем предыдущий график
        self.clear_tab(self.tab_activity)
        
        # Создаем новый график
        fig = Figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        if not activity_stats.empty:
            activity_stats.plot(kind='bar', ax=ax, title=f'New Repositories in {current_year}', color='purple')
            ax.set_ylabel('Number of new repositories')
            ax.set_xlabel('Month')
        else:
            ax.text(0.5, 0.5, f'No new repositories in {current_year}', 
                    ha='center', va='center', fontsize=12)
            ax.set_axis_off()
        
        fig.tight_layout()
        
        # Встраиваем график в Qt
        canvas = FigureCanvas(fig)
        self.activity_layout.addWidget(canvas)
        
        # Обновляем текст
        self.activity_label.setText(f"Activity analysis for {self.current_username}")
    
    def clear_tab(self, tab):
        layout = tab.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def save_report(self):
        if not hasattr(self, 'lang_stats'):
            return
            
        try:
            # Сохраняем графики
            filename_base = f"github_analysis_{self.current_username}"
            
            # Overview
            fig1, axes1 = plt.subplots(1, 2 if not self.topics_stats.empty else 1, figsize=(12, 4))
            if not self.topics_stats.empty:
                self.lang_stats.plot(kind='bar', ax=axes1[0], title='Top Languages', color='skyblue')
                self.topics_stats.plot(kind='bar', ax=axes1[1], title='Top Topics', color='lightgreen')
            else:
                self.lang_stats.plot(kind='bar', ax=axes1, title='Top Languages', color='skyblue')
            plt.tight_layout()
            plt.savefig(f"{filename_base}_overview.png")
            plt.close()
            
            # Activity
            fig2 = plt.figure(figsize=(10, 4))
            ax2 = fig2.add_subplot(111)
            if not self.activity_stats.empty:
                self.activity_stats.plot(kind='bar', ax=ax2, title=f'New Repositories in {self.current_year}', color='purple')
                ax2.set_ylabel('Number of new repositories')
                ax2.set_xlabel('Month')
            else:
                ax2.text(0.5, 0.5, f'No new repositories in {self.current_year}', 
                         ha='center', va='center', fontsize=12)
                ax2.set_axis_off()
            plt.tight_layout()
            plt.savefig(f"{filename_base}_activity.png")
            plt.close()
            
            # Сохраняем данные в CSV
            data = {
                "language": list(self.lang_stats.index),
                "count": list(self.lang_stats.values)
            }
            
            if hasattr(self, 'topics_stats') and not self.topics_stats.empty:
                data["topic"] = list(self.topics_stats.index)
                data["topic_count"] = list(self.topics_stats.values)
            
            pd.DataFrame(data).to_csv(f"{filename_base}_overview.csv", index=False)
            
            if not self.activity_stats.empty:
                activity_data = {
                    "month": self.activity_stats.index.strftime('%Y-%m'),
                    "new_repositories": self.activity_stats.values
                }
                pd.DataFrame(activity_data).to_csv(f"{filename_base}_activity.csv", index=False)
            
            QMessageBox.information(self, "Success", f"Report saved as {filename_base}_*.png and *.csv")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")
    
    def clear_results(self):
        self.username_input.clear()
        self.current_username = ""
        self.overview_label.setText("General statistics will appear here")
        self.activity_label.setText("Activity analysis will appear here")
        self.save_btn.setEnabled(False)
        
        self.clear_tab(self.tab_overview)
        self.clear_tab(self.tab_activity)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установим стиль
    app.setStyle('Fusion')
    
    window = GitHubAnalyzer()
    window.show()
    
    sys.exit(app.exec_())
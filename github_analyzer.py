from github import Github, RateLimitExceededException, BadCredentialsException
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox
import os

class GitHubAnalyzer:
    def __init__(self, ui):
        self.ui = ui
        self.current_username = ""
        self.cache = {}
        self.lang_stats = None
        self.topics_stats = None
        self.activity_stats = None
        self.current_year = datetime.now().year
        self.setup_connections()

    def setup_connections(self):
        """Подключаем сигналы кнопок к методам"""
        self.ui.analyze_btn.clicked.connect(self.analyze_profile)
        self.ui.save_btn.clicked.connect(self.save_report)
        self.ui.clear_btn.clicked.connect(self.clear_results)

    def analyze_profile(self):
        """Анализ GitHub профиля"""
        if not self.ui.token:
            reply = QMessageBox.question(
                self.ui, 
                "No Token", 
                "You're using limited guest access (60 requests/hour).\n"
                "Do you want to enter a token for full access?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.ui.show_token_dialog()
                return
        
        username = self.ui.username_input.text().strip()
        if not username:
            QMessageBox.warning(self.ui, "Error", "Please enter a GitHub username")
            return
        
        try:
            self.current_username = username
            g = Github(self.ui.token) if self.ui.token else Github()
            
            try:
                user = g.get_user(username)
            except BadCredentialsException:
                QMessageBox.critical(self.ui, "Invalid Token", 
                    "The saved token is invalid!\n"
                    "Please update your GitHub token in settings.")
                self.ui.token = None
                return
            
            self.ui.progress.show()
            self.ui.progress.setValue(0)
            QApplication.processEvents()
            
            repos = list(user.get_repos())
            total_repos = len(repos)
            self.ui.progress.setMaximum(total_repos)
            
            languages = []
            repo_topics = []
            repo_dates = []
            
            for i, repo in enumerate(repos):
                if not repo.fork:
                    if repo.language:
                        languages.append(repo.language)
                    repo_topics.extend(repo.get_topics())
                    repo_dates.append(repo.created_at)
                
                self.ui.progress.setValue(i + 1)
                QApplication.processEvents()
            
            # Анализ данных
            self.lang_stats = pd.Series(languages).value_counts().head(5)
            self.topics_stats = pd.Series(repo_topics).value_counts().head(5)
            
            repo_dates_this_year = [d for d in repo_dates if d.year == self.current_year]
            
            if repo_dates_this_year:
                activity_df = pd.DataFrame({'date': repo_dates_this_year})
                activity_df['date'] = pd.to_datetime(activity_df['date'])
                self.activity_stats = activity_df.resample('ME', on='date').size() 
            else:
                self.activity_stats = pd.Series(dtype=int)
            
            # Показ результатов
            self.show_results()
            self.ui.save_btn.setEnabled(True)
            
        except RateLimitExceededException:
            reset_time = datetime.fromtimestamp(g.rate_limiting_resettime)
            wait_time = reset_time - datetime.now()
            QMessageBox.critical(
                self.ui, 
                "API Limit Exceeded",
                f"Try again in {wait_time.seconds//60} minutes\n"
                f"(after {reset_time.strftime('%H:%M:%S')})"
            )
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Analysis failed: {str(e)}")
        finally:
            self.ui.progress.hide()

    def show_results(self):
        """Отображение результатов анализа"""
        # Очистка предыдущих результатов
        self.ui.clear_tab(self.ui.tab_overview)
        self.ui.clear_tab(self.ui.tab_activity)
        
        # График языков и тегов
        fig1, axes1 = plt.subplots(1, 2 if not self.topics_stats.empty else 1, figsize=(10, 4))
        
        if self.topics_stats.empty:
            ax = axes1
        else:
            ax = axes1[0]
        
        self.lang_stats.plot(kind='bar', ax=ax, title='Top Languages', color='skyblue')
        ax.set_ylabel('Count')
        
        if not self.topics_stats.empty:
            self.topics_stats.plot(kind='bar', ax=axes1[1], title='Top Topics', color='lightgreen')
            axes1[1].set_ylabel('Count')
        
        fig1.tight_layout()
        canvas1 = FigureCanvas(fig1)
        self.ui.overview_layout.addWidget(canvas1)
        self.ui.overview_label.setText(f"General statistics for {self.current_username}")
        
        # График активности
        fig2 = Figure(figsize=(10, 4))
        ax2 = fig2.add_subplot(111)
        
        if not self.activity_stats.empty:
            self.activity_stats.plot(kind='bar', ax=ax2, title=f'New Repositories in {self.current_year}', color='purple')
            ax2.set_ylabel('Number of new repositories')
            ax2.set_xlabel('Month')
        else:
            ax2.text(0.5, 0.5, f'No new repositories in {self.current_year}', 
                    ha='center', va='center', fontsize=12)
            ax2.set_axis_off()
        
        fig2.tight_layout()
        canvas2 = FigureCanvas(fig2)
        self.ui.activity_layout.addWidget(canvas2)
        self.ui.activity_label.setText(f"Activity analysis for {self.current_username}")

    def save_report(self):
        """Сохранение отчёта в файлы"""
        if not self.current_username:
            QMessageBox.warning(self.ui, "Error", "No data to save. Analyze a profile first.")
            return
        
        try:
            base_name = f"github_analysis_{self.current_username}"
            
            # Сохранение графиков
            plt.figure(figsize=(10, 4))
            if not self.topics_stats.empty:
                plt.subplot(121)
            self.lang_stats.plot(kind='bar', title='Top Languages', color='skyblue')
            plt.ylabel('Count')
            
            if not self.topics_stats.empty:
                plt.subplot(122)
                self.topics_stats.plot(kind='bar', title='Top Topics', color='lightgreen')
                plt.ylabel('Count')
            
            plt.tight_layout()
            plt.savefig(f"{base_name}_overview.png")  # Для изображений кодировка не нужна
            plt.close()
            
            # График активности
            plt.figure(figsize=(10, 4))
            if not self.activity_stats.empty:
                self.activity_stats.plot(kind='bar', title=f'New Repositories in {self.current_year}', color='purple')
                plt.ylabel('Number of new repositories')
                plt.xlabel('Month')
            else:
                plt.text(0.5, 0.5, f'No new repositories in {self.current_year}', 
                        ha='center', va='center', fontsize=12)
                plt.axis('off')
            
            plt.tight_layout()
            plt.savefig(f"{base_name}_activity.png")
            plt.close()
            
            # Сохранение данных в CSV с UTF-8
            data = {
                "language": list(self.lang_stats.index),
                "count": list(self.lang_stats.values)
            }
            
            if not self.topics_stats.empty:
                data["topic"] = list(self.topics_stats.index)
                data["topic_count"] = list(self.topics_stats.values)
            
            # Важное изменение: явно указываем UTF-8 и обработку ошибок
            pd.DataFrame(data).to_csv(
                f"{base_name}_overview.csv", 
                index=False,
                encoding='utf-8',
                errors='replace'  # Заменяет проблемные символы на '?'
            )
            
            if not self.activity_stats.empty:
                activity_data = {
                    "month": self.activity_stats.index.strftime('%Y-%m'),
                    "new_repositories": self.activity_stats.values
                }
                pd.DataFrame(activity_data).to_csv(
                    f"{base_name}_activity.csv", 
                    index=False,
                    encoding='utf-8',
                    errors='replace'
                )
            
            QMessageBox.information(
                self.ui, 
                "Success", 
                f"Report saved as:\n"
                f"{base_name}_overview.png\n"
                f"{base_name}_activity.png\n"
                f"{base_name}_overview.csv\n"
                f"{base_name}_activity.csv"
            )
            
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to save report: {str(e)}")

    def clear_results(self):
        """Очистка результатов"""
        self.current_username = ""
        self.lang_stats = None
        self.topics_stats = None
        self.activity_stats = None
        
        self.ui.username_input.clear()
        self.ui.overview_label.setText("General statistics will appear here")
        self.ui.activity_label.setText("Activity analysis will appear here")
        self.ui.save_btn.setEnabled(False)
        
        self.ui.clear_tab(self.ui.tab_overview)
        self.ui.clear_tab(self.ui.tab_activity)

import sys
from PyQt5.QtWidgets import QApplication
from ui import GitHubAnalyzerUI
from github_analyzer import GitHubAnalyzer
from styles import apply_style

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_style(app)
    
    # Create UI
    ui = GitHubAnalyzerUI()
    
    # Create analyzer and connect it to UI
    analyzer = GitHubAnalyzer(ui)
    
    # Show window
    ui.show()
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {e}")

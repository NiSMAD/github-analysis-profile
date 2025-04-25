STYLES = """
QMainWindow {
    background-color: #f0f0f0;
    font-family: 'Segoe UI';
}

QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #45a049;
}

QLineEdit {
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
    min-width: 200px;
}

QProgressBar {
    border: 1px solid #ccc;
    border-radius: 4px;
    text-align: center;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    width: 10px;
}

QTabWidget::pane {
    border-top: 1px solid #ccc;
}
"""

def apply_style(app):
    app.setStyle("Fusion")
    app.setStyleSheet(STYLES)

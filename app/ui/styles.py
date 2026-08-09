"""
Modern Dark Theme QSS Stylesheet and Custom Color Palette for PyQt6.
Catppuccin Macchiato / Premium Dark Aesthetic.
"""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #181825;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QWidget {
    background-color: #181825;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Header & Toolbars */
QToolBar {
    background-color: #1e1e2e;
    border-bottom: 1px solid #313244;
    padding: 6px;
    spacing: 10px;
}

/* Push Buttons */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #89b4fa;
    color: #11111b;
}

QPushButton#accentButton {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
}

QPushButton#accentButton:hover {
    background-color: #b4befe;
}

/* Table Widget */
QTableWidget {
    background-color: #1e1e2e;
    alternate-background-color: #181825;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 8px;
    selection-background-color: #45475a;
    selection-color: #ffffff;
    font-size: 13px;
}

QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #313244;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}

/* Metric Cards */
QFrame#metricCard {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 12px;
}

QLabel#metricTitle {
    color: #a6adc8;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel#metricValue {
    color: #89b4fa;
    font-size: 24px;
    font-weight: bold;
}

QLabel#metricSubtext {
    color: #6c7086;
    font-size: 11px;
}

/* Tab Widget & Side Panels */
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 8px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
}

/* Status Badges */
QLabel#badgeBuy {
    background-color: rgba(166, 227, 161, 0.2);
    color: #a6e3a1;
    border: 1px solid #a6e3a1;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: bold;
}

QLabel#badgeSell {
    background-color: rgba(243, 139, 168, 0.2);
    color: #f38ba8;
    border: 1px solid #f38ba8;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: bold;
}

QLabel#badgeAccept {
    background-color: rgba(166, 227, 161, 0.25);
    color: #a6e3a1;
    border: 1px solid #a6e3a1;
    border-radius: 4px;
    padding: 2px 6px;
    font-weight: bold;
}

QLabel#badgeReject {
    background-color: rgba(243, 139, 168, 0.25);
    color: #f38ba8;
    border: 1px solid #f38ba8;
    border-radius: 4px;
    padding: 2px 6px;
    font-weight: bold;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #181825;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}
"""

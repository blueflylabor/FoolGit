"""
FoolGit 暗黑极简程序员主题与样式工具模块 (Dark/Charcoal Minimalist Theme)
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QDialog

DARK_QSS = """
QMainWindow, QWidget#MainWidget {
    background-color: #121316;
    color: #F3F4F6;
    font-family: Helvetica, Arial, sans-serif;
}

QFrame.CardFrame {
    background-color: #1C1D21;
    border: 1px solid #2B2C32;
    border-radius: 10px;
}

QFrame.TerminalFrame {
    background-color: #0A0A0C;
    border: 1px solid #222328;
    border-radius: 8px;
}

QLabel {
    color: #F3F4F6;
    font-size: 13px;
}

QLabel.Muted {
    color: #8C8F99;
    font-size: 11px;
}

QLabel.SectionTitle {
    color: #8C8F99;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* 按钮基础样式 */
QPushButton {
    background-color: #27282D;
    color: #E4E7EB;
    border: 1px solid #36373E;
    border-radius: 7px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #32333A;
    border-color: #4A4B54;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #1F2024;
}

QPushButton:disabled {
    background-color: #1B1C20;
    color: #555863;
    border-color: #25262C;
}

/* 一键同步按钮 (Emerald Accent) */
QPushButton#SyncButton {
    background-color: #10B981;
    color: #FFFFFF;
    border: 1px solid #059669;
    font-size: 14px;
    font-weight: 700;
    padding: 12px 20px;
    border-radius: 8px;
}

QPushButton#SyncButton:hover {
    background-color: #059669;
    border-color: #047857;
}

QPushButton#SyncButton:pressed {
    background-color: #047857;
}

QPushButton#SyncButton:disabled {
    background-color: #14533D;
    color: #9CA3AF;
    border-color: #114231;
}

/* 后悔药/危险按钮 (Danger Accent) */
QPushButton#UndoButton {
    background-color: #2A1D20;
    color: #F87171;
    border: 1px solid #4D2529;
}

QPushButton#UndoButton:hover {
    background-color: #3B2227;
    border-color: #6E3036;
    color: #FCA5A5;
}

/* 语言切换标签按钮 */
QPushButton#LangButton {
    background-color: #1E2024;
    color: #9CA3AF;
    border: 1px solid #2E3036;
    padding: 4px 10px;
    font-size: 11px;
    border-radius: 6px;
}

QPushButton#LangButton:hover {
    background-color: #2A2C33;
    color: #FFFFFF;
    border-color: #3F424A;
}

/* 输入框 */
QLineEdit {
    background-color: #121316;
    border: 1px solid #2D2E35;
    border-radius: 7px;
    padding: 9px 12px;
    color: #F3F4F6;
    font-size: 13px;
    selection-background-color: #2563EB;
}

QLineEdit:focus {
    border: 1px solid #3B82F6;
    background-color: #16171B;
}

/* 下拉菜单 */
QComboBox {
    background-color: #222328;
    color: #E4E7EB;
    border: 1px solid #32333A;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
}

QComboBox:hover {
    border-color: #44454E;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1C1D21;
    color: #E4E7EB;
    border: 1px solid #32333A;
    selection-background-color: #2B2C32;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}

/* 控制台日志窗口 */
QTextEdit#LogConsole {
    background-color: #0A0A0C;
    color: #A7F3D0;
    border: none;
    font-family: Menlo, Monaco, Courier, monospace;
    font-size: 11.5px;
    line-height: 1.4;
    padding: 8px;
}

/* 列表控件 */
QListWidget {
    background-color: #0A0A0C;
    border: 1px solid #2B2C32;
    border-radius: 8px;
    color: #E4E7EB;
    padding: 4px;
}

QListWidget::item {
    padding: 6px 10px;
    border-radius: 5px;
}

QListWidget::item:selected {
    background-color: #27282D;
    color: #FFFFFF;
}

QListWidget::item:hover {
    background-color: #1F2024;
}

/* 极简暗黑滚动条 */
QScrollBar:vertical {
    background: #121316;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2E3038;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #40434E;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 状态胶囊 */
QLabel#StatusPill {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}
"""


def create_app_icon() -> QIcon:
    """生成极简暗黑科技风应用图标"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#10B981"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
    painter.setPen(QColor("#121316"))
    painter.setFont(QFont("Helvetica", 30, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⚡")
    painter.end()
    return QIcon(pixmap)


def create_dark_dialog(parent, title: str, width: int, height: int, fixed: bool = True) -> QDialog:
    """创建统一暗黑极简风格的模态弹窗"""
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    if fixed:
        dialog.setFixedSize(width, height)
    else:
        dialog.resize(width, height)
    dialog.setStyleSheet("background-color: #1C1D21; color: #F3F4F6;")
    return dialog


def render_diff_html(widget, raw_diff: str, empty_msg: str = "") -> None:
    """将统一 diff 文本高亮渲染到 QTextEdit（复用视图逻辑避免重复）"""
    widget.clear()
    if not raw_diff:
        if empty_msg:
            widget.append(f"<span style='color: #10B981;'>{empty_msg}</span>")
        return

    for line in raw_diff.splitlines():
        safe_l = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if safe_l.startswith("+++") or safe_l.startswith("---"):
            widget.append(f"<span style='color: #9CA3AF; font-weight: bold;'>{safe_l}</span>")
        elif safe_l.startswith("+"):
            widget.append(f"<span style='color: #34D399;'>{safe_l}</span>")
        elif safe_l.startswith("-"):
            widget.append(f"<span style='color: #F87171;'>{safe_l}</span>")
        elif safe_l.startswith("@@"):
            widget.append(f"<span style='color: #38BDF8;'>{safe_l}</span>")
        elif safe_l.startswith("commit "):
            widget.append(f"<span style='color: #FBBF24; font-weight: bold;'>{safe_l}</span>")
        else:
            widget.append(f"<span style='color: #D1D5DB;'>{safe_l}</span>")

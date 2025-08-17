import sys
import math
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QMessageBox
import webbrowser
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QAction
from PySide6.QtCore import Qt, QPoint, QRectF

# --- Configuration from Final SVG ---
WINDOW_WIDTH = 124
WINDOW_HEIGHT = 105

# Colors from the final SVG design
COLOR_FRAME = QColor("#C0BEB3")
COLOR_FRAME_BORDER = QColor("#FFFFFF")
COLOR_DISPLAY_BG = QColor("#FFFFFF")
COLOR_TEXT_NUMBER = QColor("#000000")
COLOR_PLUS_BG = QColor("#63BAAA")
COLOR_MINUS_BG = QColor("#8B275D")
COLOR_CLOSE_BG = QColor("#000000")
COLOR_RESET_BG = QColor("#000000")
COLOR_ICON_WHITE = QColor("#FFFFFF") # New color for all icons
TAB_DOT_COLORS = [QColor(c) for c in ["#F7D474", "#E09322", "#A1413F", "#484366", "#6BB09A"]]

class CounterApp(QWidget):
    """
    A frameless, floating desktop counter application built with PySide6
    for high-quality, anti-aliased rendering.
    """
    def __init__(self):
        super().__init__()
        # --- State Management ---
        self.active_tab = 0
        self.counters = [0] * 5
        self.drag_position = None

        self.setup_ui()
        self.repo_url = "https://github.com/pertamaks/floating-counter"

    def setup_ui(self):
        """Configures the window properties."""
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # --- Create a Frameless, Transparent, Always-on-Top Window ---
        self.setWindowFlags(
            Qt.FramelessWindowHint |    # No title bar or borders
            Qt.WindowStaysOnTopHint  # Always on top
            #Qt.Tool                     # Doesn't show up in the task bar
        )
        self.setAttribute(Qt.WA_TranslucentBackground) # Makes background transparent

    def paintEvent(self, event):
        """
        This method is called whenever the widget needs to be redrawn.
        All drawing happens here using QPainter for high quality results.
        """
        painter = QPainter(self)
        # Enable Anti-aliasing for smooth shapes and text
        painter.setRenderHint(QPainter.Antialiasing)

        # --- Draw Main Frame ---
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(COLOR_FRAME))
        painter.drawRoundedRect(QRectF(15, 10, 94, 87), 14, 14)

        pen = QPen(COLOR_FRAME_BORDER, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(13.5, 8.5, 97, 90), 15.5, 15.5)

        # --- Draw Inner Display ---
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(COLOR_DISPLAY_BG))
        painter.drawRoundedRect(QRectF(22, 23, 80, 68), 7, 7)

        # --- Draw Counter Number ---
        # Use "Inter" font if available, with a fallback
        font = QFont("Inter", 42, QFont.Weight.ExtraBold)
        painter.setFont(font)
        painter.setPen(QPen(COLOR_TEXT_NUMBER))
        display_text = f"{self.counters[self.active_tab]:02d}"
        painter.drawText(QRectF(22, 23, 80, 68), Qt.AlignCenter, display_text)
        
        # --- Draw Tabs and Buttons ---
        self.draw_tabs(painter)
        self.draw_buttons(painter)

    def draw_tabs(self, painter):
        """Draws the 5 colored tab dots."""
        dot_x_coords = [36, 49, 62, 74, 87]
        painter.setPen(Qt.NoPen)
        for i, x in enumerate(dot_x_coords):
            painter.setBrush(QBrush(TAB_DOT_COLORS[i]))
            painter.drawEllipse(QPoint(x, 16), 4, 4)
            if i == self.active_tab:
                pen = QPen(QColor("white"), 1.5)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QPoint(x, 16), 5, 5)
                painter.setPen(Qt.NoPen) # Reset pen

    def draw_buttons(self, painter):
        """Draws the four control buttons with colored fills and white borders."""
        # --- Plus Button ---
        painter.setBrush(QBrush(COLOR_PLUS_BG))
        painter.setPen(QPen(COLOR_ICON_WHITE, 3)) # Set white border
        painter.drawEllipse(QPoint(109, 74), 14, 14) # Draw the colored circle with border
        pen = QPen(COLOR_ICON_WHITE, 2.5, Qt.SolidLine, Qt.RoundCap) # Pen for the icon
        painter.setPen(pen)
        painter.drawLine(109, 68, 109, 80)
        painter.drawLine(103, 74, 115, 74)

        # --- Minus Button ---
        painter.setBrush(QBrush(COLOR_MINUS_BG))
        painter.setPen(QPen(COLOR_ICON_WHITE, 3))
        painter.drawEllipse(QPoint(15, 74), 14, 14)
        pen.setColor(COLOR_ICON_WHITE) # Pen is already white, but good practice
        painter.setPen(pen)
        painter.drawLine(9, 74, 21, 74)
        
        # --- Close Button ---
        painter.setBrush(QBrush(COLOR_CLOSE_BG))
        painter.setPen(QPen(COLOR_ICON_WHITE, 3))
        painter.drawEllipse(QPoint(109, 12), 11, 11)
        painter.setPen(QPen(COLOR_ICON_WHITE))
        painter.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        painter.drawText(QRectF(97, -2, 24, 24), Qt.AlignCenter, "✕")

        # --- Reset Button ---
        painter.setBrush(QBrush(COLOR_RESET_BG))
        painter.setPen(QPen(COLOR_ICON_WHITE, 3))
        painter.drawEllipse(QPoint(22, 93), 11, 11)
        painter.setPen(QPen(COLOR_ICON_WHITE))
        painter.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        painter.drawText(QRectF(10, 78, 24, 24), Qt.AlignCenter, "⟳")

    def mousePressEvent(self, event):
        """Handles mouse clicks for buttons, tabs, and dragging."""
        if event.button() == Qt.LeftButton:
            pos = event.position()
            
            # Check Tab clicks
            dot_x_coords = [36, 49, 62, 74, 87]
            for i, dot_x in enumerate(dot_x_coords):
                if math.sqrt((pos.x() - dot_x)**2 + (pos.y() - 16)**2) <= 5:
                    if self.active_tab != i:
                        self.active_tab = i
                        self.update() # Trigger a repaint
                    return

            # Check Button clicks
            if math.sqrt((pos.x() - 109)**2 + (pos.y() - 74)**2) <= 15: # Plus
                if self.counters[self.active_tab] < 99:
                    self.counters[self.active_tab] += 1
            elif math.sqrt((pos.x() - 15)**2 + (pos.y() - 74)**2) <= 15: # Minus
                if self.counters[self.active_tab] > 0:
                    self.counters[self.active_tab] -= 1
            elif math.sqrt((pos.x() - 22)**2 + (pos.y() - 93)**2) <= 12: # Reset
                self.counters[self.active_tab] = 0
            elif math.sqrt((pos.x() - 109)**2 + (pos.y() - 12)**2) <= 12: # Close
                QApplication.instance().quit()
                return
            else: # If no button is clicked, start dragging
                self.drag_position = event.globalPosition().toPoint()
                return
            
            self.update() # Trigger a repaint if a counter changed

        elif event.button() == Qt.RightButton:
            pos = event.position()
            # Only show copyright if right-click is on the counter display
            display_rect = QRectF(22, 23, 80, 68)
            if display_rect.contains(pos):
                self.show_copyright_menu(event.globalPosition().toPoint())

    def show_copyright_menu(self, global_pos):
        menu = QMenu(self)
        action = QAction("© 2025 pertamaks/floating-counter", self)
        menu.addAction(action)
        def open_repo():
            webbrowser.open(self.repo_url)
        action.triggered.connect(open_repo)
        menu.exec(global_pos)

    def mouseMoveEvent(self, event):
        """Handles window dragging."""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_position)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        """Resets the drag position."""
        self.drag_position = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CounterApp()
    window.show()
    sys.exit(app.exec())

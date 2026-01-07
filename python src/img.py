import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QFileDialog, QHBoxLayout, 
                             QLabel, QLineEdit)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QImage, QPainter, QColor, QPixmap, QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FullMonoScannerV3(QMainWindow):
    def __init__(self):
        super().__init__()
        
        icon_path = resource_path("d.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setWindowTitle("MONO_SCANNER_ULTIMATE")
        self.resize(600, 500)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: #050505;
                color: #ffffff;
                font-family: 'Consolas', monospace;
            }
        """)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(15)

        top_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Paste folder path here...")
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #000;
                border: 1px solid #333;
                padding: 10px;
                color: #00ff00;
                font-size: 13px;
            }
        """)
        
        self.btn_select = QPushButton("BROWSE")
        self.btn_select.setFixedWidth(100)
        self.btn_select.setStyleSheet(self.get_btn_style())
        self.btn_select.clicked.connect(self.select_folder)

        top_layout.addWidget(self.path_input)
        top_layout.addWidget(self.btn_select)
        self.main_layout.addLayout(top_layout)

        self.btn_scan = QPushButton("EXECUTE_SCAN_AND_GENERATE_TREE")
        self.btn_scan.setStyleSheet(self.get_btn_style())
        self.btn_scan.clicked.connect(self.scan_folder)
        self.main_layout.addWidget(self.btn_scan)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                border: 1px solid #222;
                padding: 15px;
                color: #ccc;
                font-size: 12px;
            }
        """)
        self.main_layout.addWidget(self.output_display)

        export_layout = QHBoxLayout()
        self.btn_export_txt = QPushButton("SAVE_TXT")
        self.btn_export_txt.setStyleSheet(self.get_btn_style())
        self.btn_export_txt.clicked.connect(self.export_txt)
        
        self.btn_export_png = QPushButton("SAVE_FULL_IMAGE (PNG)")
        self.btn_export_png.setStyleSheet(self.get_btn_style())
        self.btn_export_png.clicked.connect(self.export_full_png)

        export_layout.addWidget(self.btn_export_txt)
        export_layout.addWidget(self.btn_export_png)
        self.main_layout.addLayout(export_layout)

    def get_btn_style(self):
        return """
            QPushButton {
                background-color: #111;
                border: 1px solid #444;
                color: #fff;
                padding: 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fff;
                color: #000;
            }
        """

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.path_input.setText(path)

    def generate_tree(self, root_dir, prefix=""):
        tree = []
        try:
            items = sorted(os.listdir(root_dir))
        except: return [f"{prefix}└── [ACCESS_DENIED]"]
            
        for i, name in enumerate(items):
            if name.startswith('.'): continue
            path = os.path.join(root_dir, name)
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            tree.append(f"{prefix}{connector}{name}")
            if os.path.isdir(path):
                ext = "    " if is_last else "│   "
                tree.extend(self.generate_tree(path, prefix + ext))
        return tree

    def scan_folder(self):
        target = self.path_input.text()
        if not os.path.exists(target):
            self.output_display.setPlainText("!! INVALID_PATH")
            return
        
        lines = [f"PROJECT_ROOT: {os.path.basename(target)}/"] + self.generate_tree(target)
        self.output_display.setPlainText("\n".join(lines))

    def export_txt(self):
        content = self.output_display.toPlainText()
        if not content: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save TXT", "", "TXT (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def export_full_png(self):
        content = self.output_display.toPlainText()
        if not content: return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Full Image", "", "PNG (*.png)")
        if not file_path: return

        lines = content.split('\n')
        font = QFont("Consolas", 12)
        line_height = 20
        margin = 40
        img_width = 1200 
        img_height = (len(lines) * line_height) + (margin * 2)

        image = QImage(QSize(img_width, img_height), QImage.Format_RGB32)
        image.fill(QColor("#050505")) 

        painter = QPainter(image)
        painter.setPen(QColor("#00ff00")) 
        painter.setFont(font)

        for i, line in enumerate(lines):
            painter.drawText(margin, margin + (i * line_height), line)
        
        painter.end()
        image.save(file_path, "PNG")
        self.output_display.append("\n>> FULL_IMAGE_EXPORTED_SUCCESSFULLY")

# المنطق الجديد لدعم ميزة scan .
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FullMonoScannerV3()
    
    # التحقق من وجود Argument (مسار ممرر)
    if len(sys.argv) > 1:
        raw_path = sys.argv[1]
        # إذا كانت المدخلات "." نستخدم مسار العمل الحالي
        final_path = os.getcwd() if raw_path == "." else os.path.abspath(raw_path)
        
        if os.path.exists(final_path):
            window.path_input.setText(final_path)
            # تنفيذ المسح فوراً عند التشغيل من سطر الأوامر
            window.scan_folder()

    window.show()
    sys.exit(app.exec())
import subprocess
import webbrowser
from pathlib import Path

from qt_compat import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QTabWidget,
    QTextEdit, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QComboBox,
    QMessageBox, QAction, QKeySequence, QFileDialog, QStatusBar, Qt
)

from editor import EditorTab
from editor.runner import RunnerThread, get_run_command
from config.languages import LANG_CONFIG
from utils.workspace import populate_tree

class MochaCodespace(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mocha Codespace")
        self.setGeometry(100, 100, 1200, 800)

        self.workspace_path = None
        self.runner_thread = None

        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()

        self.new_file()

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #faf7f2; }
            QMenuBar { background-color: #f5ebe0; color: #704241; padding: 4px; }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("📁 Workspace")
        self.tree_widget.itemDoubleClicked.connect(self.on_tree_double_click)
        self.tree_widget.hide()

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        right_layout.addWidget(self.tab_widget)

        console_label = QLabel("💻 Console Output:")
        right_layout.addWidget(console_label)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(200)
        right_layout.addWidget(self.console)

        self.main_splitter.addWidget(right_widget)

    def create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")
        # simple placeholders for undo/redo/find
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        run_menu = menubar.addMenu("&Run")
        run_action = QAction("&Run", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction("📄 New", self.new_file)
        toolbar.addAction("📂 Open", self.open_file)
        toolbar.addAction("💾 Save", self.save_file)
        toolbar.addSeparator()

        lang_label = QLabel(" 🔤 Language: ")
        toolbar.addWidget(lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(LANG_CONFIG.keys()))
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        toolbar.addWidget(self.lang_combo)
        toolbar.addSeparator()
        toolbar.addAction("▶️ Run", self.run_code)
        toolbar.addSeparator()
        toolbar.addAction("📁 Open Workspace", self.open_workspace)
        toolbar.addAction("❌ Close Workspace", self.close_workspace)

    def create_statusbar(self):
        self.statusBar().showMessage("Ready")

    def new_file(self):
        language = self.lang_combo.currentText()
        if not language:
            language = "Python"
        tab = EditorTab(language=language)
        ext = LANG_CONFIG.get(language, {}).get("ext", "")
        title = f"untitled{ext}"
        idx = self.tab_widget.addTab(tab, title)
        self.tab_widget.setCurrentIndex(idx)
        self.statusBar().showMessage(f"New {language} file created")

    def open_file(self, filepath=None):
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if not filepath:
            return
        path = Path(filepath)
        ext = path.suffix.lower()
        language = "Python"
        for lang, cfg in LANG_CONFIG.items():
            if cfg.get("ext") == ext:
                language = lang
                break
        tab = EditorTab(language=language, filepath=path)
        idx = self.tab_widget.addTab(tab, path.name)
        self.tab_widget.setCurrentIndex(idx)
        self.statusBar().showMessage(f"Opened {path}")

    def save_file(self):
        tab = self.get_current_tab()
        if not tab:
            return
        if not tab.filepath:
            return self.save_file_as()
        if tab.save():
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab.filepath.name)
            self.statusBar().showMessage(f"Saved {tab.filepath}")
            self.console.append(f"Saved: {tab.filepath}\n")

    def save_file_as(self):
        tab = self.get_current_tab()
        if not tab:
            return
        ext = LANG_CONFIG.get(tab.language, {}).get("ext", "")
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File As", f"untitled{ext}", "All Files (*)")
        if filepath and tab.save(filepath):
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab.filepath.name)
            self.statusBar().showMessage(f"Saved as {tab.filepath}")
            self.console.append(f"Saved as: {tab.filepath}\n")

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self, "Close Tab", "Cannot close the last tab")

    def get_current_tab(self):
        widget = self.tab_widget.currentWidget()
        return widget if isinstance(widget, EditorTab) else None

    def on_language_changed(self, language):
        tab = self.get_current_tab()
        if tab and not tab.filepath:
            tab.language = language
            tab.editor.set_language(language)
            tab.load_content()

    def undo(self):
        tab = self.get_current_tab()
        if tab:
            tab.editor.undo()

    def redo(self):
        tab = self.get_current_tab()
        if tab:
            tab.editor.redo()

    def run_code(self):
        tab = self.get_current_tab()
        if not tab:
            return
        if not tab.filepath:
            reply = QMessageBox.question(self, "Save File", "File must be saved before running. Save now?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_file_as()
            else:
                return
        if not tab.filepath:
            return

        self.console.clear()
        self.console.append(f"Running {tab.filepath.name} ({tab.language})...\n")
        self.statusBar().showMessage("Running...")

        cfg = LANG_CONFIG.get(tab.language, {})
        runner = cfg.get("runner")
        try:
            command = get_run_command(tab.filepath, tab.language, runner)
        except RuntimeError as e:
            self.console.append(str(e) + "\n")
            self.statusBar().showMessage("Ready")
            return

        if command is None:
            # runner handled (like opening in browser) or fallback
            self.statusBar().showMessage("Ready")
            return

        self.runner_thread = RunnerThread(command, str(tab.filepath.parent))
        self.runner_thread.output.connect(self.console.append)
        self.runner_thread.finished.connect(lambda: self.statusBar().showMessage("Ready"))
        self.runner_thread.start()

    def open_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace")
        if not folder:
            return
        self.workspace_path = Path(folder)
        if not self.tree_widget.isVisible():
            self.main_splitter.insertWidget(0, self.tree_widget)
            self.tree_widget.show()
            self.main_splitter.setSizes([250, 950])
        self.tree_widget.clear()
        populate_tree(self.workspace_path, self.tree_widget)
        self.statusBar().showMessage(f"Opened workspace: {self.workspace_path}")

    def on_tree_double_click(self, item, column):
        filepath = item.data(0, Qt.ItemDataRole.UserRole)
        if filepath:
            path = Path(filepath)
            if path.is_file():
                self.open_file(str(path))

    def close_workspace(self):
        if self.workspace_path:
            self.tree_widget.hide()
            self.workspace_path = None
            self.statusBar().showMessage("Workspace closed")

    def show_about(self):
        QMessageBox.about(
            self,
            "About Mocha Codespace",
            """<h2>Mocha Codespace 0.4</h2>
            <p>A modern, beginner-friendly IDE built with PyQt6/PySide6</p>
            <p><b>Features:</b></p>
            <ul>
                <li>✨ Syntax highlighting for all supported languages</li>
                <li>🔤 Smart autocompletion (Ctrl+Space)</li>
                <li>📝 Auto-indentation</li>
                <li>🎨 Beautiful Mocha color theme</li>
            </ul>
            <p><b>Supported Languages:</b></p>
            <ul>
                <li>Python</li>
                <li>Java</li>
                <li>C / C++</li>
                <li>JavaScript / TypeScript</li>
                <li>Rust</li>
                <li>Go</li>
                <li>C#</li>
                <li>Ruby</li>
                <li>Kotlin</li>
                <li>HTML / CSS</li>
                <li>Lua</li>
                <li>Nix</li>
                <li>Nvidia PTX</li>
            </ul>
            <p>Created with ♥ by The Mocha Foundation</p>
            <p>PyQt6/PySide6 Version</p>
            """
        )


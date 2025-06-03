import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressBar, QVBoxLayout, QWidget, QLabel
from datetime import datetime
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabBar
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mithun's Browser: The Mrowser")
        self.setGeometry(200, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
                QTabBar::tab {
                min-width: 120px;
                max-width:120px;
                height: 25px
                }
                """)
        self.add_plus_tab()
        self.new_tab_button = QToolButton()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_on_tab_switch)
        self.tabs.tabBarClicked.connect(self.handle_tab_click)
        self.setCentralWidget(self.tabs)


        self.history = [] #Each entry is(Timestamp, url)
        # Create toolbar first
        self.create_toolbar()
        

        adblocker = AdBlocker()
        QWebEngineProfile.defaultProfile().setRequestInterceptor(adblocker)
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)
        # Then add the first tab
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Navigation actions
        back_action = QAction("Back", self)
        forward_action = QAction("Forward", self)
        reload_action = QAction("Reload", self)

        back_action.triggered.connect(self.navigate_back)
        forward_action.triggered.connect(self.navigate_forward)
        reload_action.triggered.connect(self.reload_page)

        toolbar.addAction(back_action)
        toolbar.addAction(forward_action)
        toolbar.addAction(reload_action)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # New tab action
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        toolbar.addAction(new_tab_action)
        history_action = QAction("History", self)
        history_action.triggered.connect(self.show_history)
        toolbar.addAction(history_action)

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))

    def update_url_bar(self, q):
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            url_str = q.toString()
            self.url_bar.setText(url_str)
            self.tabs.setTabText(self.tabs.currentIndex(), current_browser.page().title())

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.history.append((now, url_str))


    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        plus_tab_index = self.tabs.count()-1
        if self.tabs.tabText(plus_tab_index)=="+":
            self.tabs.removeTab(plus_tab_index)

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_url_bar)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        self.add_plus_tab()
    def add_plus_tab(self):
        plus_tab = QWidget() #Dummy Widget
        i = self.tabs.addTab(plus_tab, "+")
        self.tabs.tabBar().setTabButton(i, QTabBar.RightSide, None)
    def handle_tab_click(self, index):
        if self.tabs.tabText(index)=="+":
            self.add_new_tab()
    def update_url_on_tab_switch(self, i):
        if i >= 0:
            current_browser = self.tabs.widget(i)
            if current_browser and self.url_bar:
                self.url_bar.setText(current_browser.url().toString())

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def handle_download(self, download: QWebEngineDownloadItem):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path(), options=options)
        if path:
            download.setPath(path)
            download.accept()

            # Keep widget alive by assigning to instance
            self.download_widget = QWidget(self)
            layout = QVBoxLayout()
            label = QLabel(f"Downloading: {path}")
            progress = QProgressBar()
            progress.setMaximum(100)
            layout.addWidget(label)
            layout.addWidget(progress)
            self.download_widget.setLayout(layout)
            self.download_widget.setWindowTitle("Download in Progress")
            self.download_widget.resize(400, 100)
            self.download_widget.show()

            download.downloadProgress.connect(
                lambda rec, tot: progress.setValue(int((rec / tot) * 100)) if tot > 0 else None
            )
            download.finished.connect(self.download_widget.close)
    def show_history(self):
        self.history_window = QWidget(self)  # Persist as attribute to prevent garbage collection
        self.history_window.setWindowTitle("Browsing History")
        layout = QVBoxLayout()

        for timestamp, url in reversed(self.history):
            label = QLabel(f"{timestamp} — <a href='{url}'>{url}</a>")
            label.setOpenExternalLinks(False)
            label.linkActivated.connect(self.make_history_link_handler(url))
            layout.addWidget(label)

        self.history_window.setLayout(layout)
        self.history_window.resize(600, 400)
        self.history_window.show()

    def make_history_link_handler(self, url):
        return lambda _: self.add_new_tab(QUrl(url), "History Tab")

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.blocked_keywords = ["ads.", "doubleclick.net", "adservice.google.com", "googlesyndication", "tracking"]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(keyword in url for keyword in self.blocked_keywords):
            info.block(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
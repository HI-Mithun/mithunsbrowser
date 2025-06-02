import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QTabWidget

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mithun's Browser: The Mrowser")
        self.setGeometry(200, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_on_tab_switch)
        self.setCentralWidget(self.tabs)

        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

        self.create_toolbar()

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        back_action = QAction("Back", self)
        forward_action = QAction("Forward", self)
        reload_action = QAction("Reload", self)

        back_action.triggered.connect(self.navigate_back)
        forward_action.triggered.connect(self.navigate_forward)
        reload_action.triggered.connect(self.reload_page)

        toolbar.addAction(back_action)
        toolbar.addAction(forward_action)
        toolbar.addAction(reload_action)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        toolbar.addAction(new_tab_action)

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.reload()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            current_browser.setUrl(QUrl(url))

    def update_url_bar(self, q):
        current_browser = self.sender()  # Get the browser that emitted the signal
        if current_browser == self.tabs.currentWidget():  # Only update if it's the active tab
            self.url_bar.setText(q.toString())
            self.tabs.setTabText(self.tabs.currentIndex(), current_browser.page().title())

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_url_bar)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def update_url_on_tab_switch(self, i):
        if i >= 0:  # Check if index is valid
            current_browser = self.tabs.widget(i)
            if isinstance(current_browser, QWebEngineView):
                self.url_bar.setText(current_browser.url().toString())

    def close_tab(self, i):
        if self.tabs.count() > 1:  # Only close if more than one tab exists
            self.tabs.removeTab(i)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
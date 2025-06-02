import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

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

        # Create toolbar first
        self.create_toolbar()
        
        from PyQt5.QtWebEngineWidgets import QWebEngineProfile

        adblocker = AdBlocker()
        QWebEngineProfile.defaultProfile().setRequestInterceptor(adblocker)
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
        current_browser = self.sender()
        if current_browser == self.tabs.currentWidget() and self.url_bar:
            self.url_bar.setText(q.toString())
            self.tabs.setTabText(self.tabs.currentIndex(), current_browser.page().title()[:15])

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_url_bar)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def update_url_on_tab_switch(self, i):
        if i >= 0:
            current_browser = self.tabs.widget(i)
            if current_browser and self.url_bar:
                self.url_bar.setText(current_browser.url().toString())

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)



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
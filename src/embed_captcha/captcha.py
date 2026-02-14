from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineProfile
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QUrl, QEventLoop

from pathlib import Path
from enum import Enum

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 115Browser/35.13.0.2 Chromium/125.0"
CAPTCHA_HTML = (Path(__file__).parent / "captcha.html").read_text()

class CaptchaType(str, Enum):
    RECAPTCHA_V2 = "RECAPTCHA_V2"
    RECAPTCHA_V3 = "RECAPTCHA_V3"
    HCAPTCHA = "HCAPTCHA"

class Bridge(QObject):
    # calls when js is ready
    on_ready = pyqtSignal()

    @pyqtSlot()
    def ready(self):
        self.on_ready.emit()

    # start site_key, captcha_type
    start = pyqtSignal(str, str)

    # reset last captcha
    reset = pyqtSignal()

    on_token = pyqtSignal(str)
    on_error = pyqtSignal(str)

    @pyqtSlot(str)
    def token(self, token: str):
        self.on_token.emit(token)
    
    @pyqtSlot(str)
    def error(self, error: str):
        self.on_error.emit(error)
        
class Window(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, profile: QWebEngineProfile | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        self.profile = profile or self.temporary_profile()
        self.page = QWebEnginePage(self.profile)
        self.view.setPage(self.page)
    
    @staticmethod
    def temporary_profile(user_agent: str | None = None) -> QWebEngineProfile:
        profile = QWebEngineProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        profile.setCachePath(None)
        profile.setPersistentStoragePath(None)
        profile.setHttpUserAgent(user_agent or DEFAULT_USER_AGENT)

        return profile
    
    def closeEvent(self, a0: QCloseEvent | None) -> None:
        super().closeEvent(a0)
        self.closed.emit()

class Captcha:
    def __init__(self, site_key: str | None = None, host: QUrl | str | None = None, captcha_type: CaptchaType | None = None, title: str | None = None, profile: QWebEngineProfile | None = None):
        self.app = QApplication.instance() or QApplication([])
        
        self.window = Window(profile)
        self.window.setWindowTitle(title)
        self.page = self.window.page

        self.loop = QEventLoop()
        self.bridge = Bridge()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.page.setWebChannel(self.channel)

        self._token: str | None = None
        self._error: str | None = None
        self._ready = False
        self.bridge.on_token.connect(self._on_token)
        self.bridge.on_error.connect(self._on_error)
        self.bridge.on_ready.connect(self._on_ready)
        self.window.closed.connect(self._on_close)

        self._host: QUrl
        self._site_key: str
        self._captcha_type: CaptchaType
        self.convert(site_key, host, captcha_type)
    
    def convert(self, site_key: str | None = None, host: QUrl | str | None = None, captcha_type: CaptchaType | None = None):
        if site_key is not None:
            self._site_key = site_key
        
        if host is not None:
            self._host = QUrl(host)
            self._ready = False
            self.page.setHtml(CAPTCHA_HTML, self._host)

        if captcha_type is not None:
            self._captcha_type = captcha_type
    
    def _on_token(self, token: str | None):
        self._token = token
        self.loop.quit()
    
    def _on_error(self, error: str | None):
        self._error = error
        self.loop.quit()
    
    def _on_close(self):
        self.loop.quit()
    
    def _on_ready(self):
        if not self._ready:
            # this is pending then
            if self._site_key is not None and self._captcha_type is not None:
                self.bridge.start.emit(self._site_key, self._captcha_type)
        
        self._ready = True

    def token(self, maximize: bool = True) -> str:
        if self._captcha_type is None:
            raise ValueError("captcha type must be set")
        
        self._token = None
        self._error = None

        if maximize:
            self.window.showMaximized()
        else:
            self.window.show()

        # if we are not ready yet, self._on_ready will handle that for us
        if self._ready:
            self.bridge.start.emit(self._site_key, self._captcha_type)
        
        # block until something happens
        self.loop.exec()

        if self._token is not None:
            return self._token
        
        if self._error is not None:
            raise RuntimeError(self._error)
        
        raise KeyboardInterrupt
    
    def close(self):
        self.bridge.on_error.disconnect(self._on_error)
        self.bridge.on_token.disconnect(self._on_token)
        self.bridge.on_ready.disconnect(self._on_ready)
        self.window.closed.disconnect(self._on_close)
        self.window.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

if __name__ == "__main__":
    with Captcha(
        "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        "https://2captcha.com/demo/recaptcha-v2",
        CaptchaType.RECAPTCHA_V2
    ) as captcha:
        print(captcha.token())

        captcha.convert(site_key="b17bafa7-90bf-4070-9296-626796423086", host="https://shimuldn.github.io/hcaptcha/", captcha_type=CaptchaType.HCAPTCHA)

        print(captcha.token())
        print(captcha.token())
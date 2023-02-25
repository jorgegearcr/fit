import sys
import asyncio
import mitmproxy
import os
import tempfile
from PyQt5.QtCore import QUrl, QObject, pyqtSignal, QThread, QFile, QByteArray
import logging

from PyQt5.QtNetwork import QNetworkProxy, QSslCertificate, QSslConfiguration, QSsl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QListView
from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster


class ProxyServer(QObject):
    logging.basicConfig(filename='mitmproxy.log', level=logging.INFO)
    proxy_started = pyqtSignal(int)

    def __init__(self, port):
        super().__init__()
        self.port = port

    async def start(self):
        # setta le opzioni del proxy
        options = main.options.Options(listen_host='127.0.0.1', listen_port=self.port,
                                       ssl_insecure=True)
        master = DumpMaster(options=options)
        try:
            await master.run()
        except KeyboardInterrupt:
            master.shutdown()


class MitmThread(QThread):
    def __init__(self, port):
        super().__init__()
        self.port = port

    def run(self):
        # nuovo event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # creazione del mitmproxy
        proxy_server = ProxyServer(self.port)
        asyncio.get_event_loop().run_until_complete(proxy_server.start())


class MainWindow(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # setta la porta e starta il thread (alla creazione della mainwindow)
        port = 8081
        self.mitm_thread = MitmThread(port)
        self.mitm_thread.start()

        super().load(QUrl("https://www.google.com/"))



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # directly getting the the pem with openssl solved the problem
    # openssl pkcs12 -in {mitmproxy-ca-cert.p12} -out {cert_pem} -nodes

    with open('C:\\Users\\Routi\\Downloads\\mitmproxy-ca-cert.pem', 'rb') as f:
        pem_data = f.read()

    cert = QSslCertificate.fromData(pem_data)
    print(cert[0])

    # Create a custom SSL configuration that includes the mitmproxy certificate
    config = QSslConfiguration.defaultConfiguration()
    config.setCaCertificates(cert)
    config.setProtocol(QSsl.TlsV1_2)  # Set the SSL protocol to use (optional)


    view = MainWindow()
    view.show()
    # crea un QNetworkProxy e lo setta come proxy
    proxy = QNetworkProxy(QNetworkProxy.HttpProxy, '127.0.0.1', 8081)
    QNetworkProxy.setApplicationProxy(proxy)

    view.show()
    sys.exit(app.exec_())

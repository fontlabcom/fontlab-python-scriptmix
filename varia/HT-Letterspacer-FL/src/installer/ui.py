"""Small asynchronous FontLab installer window; downloads never block the UI."""

import shutil
import sys
from pathlib import Path

_windows = []


def refresh_scripts():
    import fontlab
    from PythonQt import QtGui

    try:
        main = fontlab.flWorkspace.instance().mainWindow
        action = main.findChild(QtGui.QAction, "actionRefreshScripts")
        if action:
            action.trigger()
            return True
    except Exception:
        pass
    return False


def run_fontlab_installer(payload, core=None, cleanup=None):
    if core is None:
        import htls_installer as core
    from PythonQt import QtCore, QtGui, QtNetwork

    payload = Path(payload)
    data = core.fontlab_data_dir()
    core.verify_payload(payload)
    lock = core.read_json(payload / "upstream.lock.json")
    expected_url = (
        "https://codeload.github.com/huertatipografica/HTLetterspacer/zip/"
        + lock["commit"]
    )
    if lock["archive"]["url"] != expected_url:
        raise ValueError("Unexpected upstream download address.")
    dialog = QtGui.QDialog()
    dialog.setWindowTitle("Install HT Letterspacer")
    dialog.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
    dialog.setFixedWidth(420)
    layout = QtGui.QVBoxLayout(dialog)
    layout.setContentsMargins(18, 18, 18, 18)
    title = QtGui.QLabel("Installing HT Letterspacer for FontLab 9")
    layout.addWidget(title)
    status = QtGui.QLabel("Downloading original HT Letterspacer…")
    status.setWordWrap(True)
    layout.addWidget(status)
    bar = QtGui.QProgressBar()
    bar.setRange(0, 0)
    layout.addWidget(bar)
    button = QtGui.QPushButton("Cancel")
    layout.addWidget(button)
    state = {
        "done": False,
        "cancelled": False,
        "result": None,
        "error": None,
        "dialog": dialog,
        "bytes": 0,
        "reply": None,
        "phase": "download",
    }
    archive = payload / "download.zip"
    manager = QtNetwork.QNetworkAccessManager(dialog)
    timeout = QtCore.QTimer(dialog)
    timeout.setSingleShot(True)
    request = QtNetwork.QNetworkRequest(QtCore.QUrl(expected_url))
    # Use Qt's native trust store. Older FontLab PythonQt bindings do not
    # expose per-request SSL configuration; never disable certificate checks.
    output = archive.open("wb")
    reply = manager.get(request)
    state["reply"] = reply
    state["manager"] = manager

    def finish(result=None, error=None):
        if state["done"]:
            return
        state["done"] = True
        state["result"], state["error"] = result, error
        timeout.stop()
        output.close()
        bar.setRange(0, 1)
        bar.setValue(1 if result else 0)
        button.setText("Done" if result else "Close")
        button.setEnabled(True)
        if result:
            refreshed = refresh_scripts()
            title.setText("HT Letterspacer " + result["version"] + " is installed")
            old = sys.modules.get("htls_fontlab")
            restart = (
                old
                and Path(old.__file__).resolve().parent
                != Path(result["runtime"]) / "htls_fontlab"
            )
            if restart:
                status.setText(
                    "Restart FontLab to activate this update. Then open Scripts → HT Letterspacer → HT Letterspacer."
                )
            else:
                status.setText(
                    "Open Scripts → HT Letterspacer → HT Letterspacer."
                    + (
                        ""
                        if refreshed
                        else "\nUse Refresh Scripts if the folder is not shown yet."
                    )
                )
            print("HTLS_INSTALL_OK " + str(result))
        else:
            title.setText("HT Letterspacer was not installed")
            status.setText(str(error) + "\nYou can run this installer again.")
            print("HTLS_INSTALL_ERROR " + str(error))
        if cleanup:
            shutil.rmtree(str(cleanup), ignore_errors=True)
        reply.deleteLater()
        state["reply"] = None
        dialog.adjustSize()

    def receive():
        if state["done"] or output.closed:
            return
        chunk = reply.readAll().data()
        state["bytes"] += len(chunk)
        if state["bytes"] > 32 * 1024 * 1024:
            state["error"] = "Upstream download is unexpectedly large."
            reply.abort()
            return
        try:
            output.write(chunk)
        except OSError as exc:
            state["error"] = str(exc)
            reply.abort()

    def progress(received, total):
        if total > 0:
            bar.setRange(0, 100)
            bar.setValue(int(100 * received / total))

    def report(message):
        if state["cancelled"] and message != "Installation complete.":
            raise RuntimeError(
                "Installation cancelled. No active installation was replaced."
            )
        status.setText(message)
        QtGui.QApplication.processEvents()

    def downloaded():
        if state["done"] or state["phase"] != "download":
            return
        state["phase"] = "finishing"
        timeout.stop()
        receive()
        output.close()
        if state["cancelled"]:
            finish(error="Installation cancelled.")
            return
        if state["error"] or reply.error() != QtNetwork.QNetworkReply.NoError:
            finish(error=state["error"] or reply.errorString())
            return
        if not str(reply.url().toString()).startswith("https://codeload.github.com/"):
            finish(error="Unexpected upstream redirect.")
            return
        try:
            state["phase"] = "install"
            # ZIP extraction and atomic file activation are short local operations.
            # The network request above is fully asynchronous on Qt's event loop.
            result = core.install(payload, data, archive=archive, progress=report)
            finish(result=result)
        except Exception as exc:
            finish(error=str(exc))

    def clicked():
        if state["done"]:
            dialog.close()
        else:
            state["cancelled"] = True
            button.setEnabled(False)
            status.setText("Cancelling…")
            if state["phase"] == "download":
                reply.abort()

    def closed(*args):
        if not state["done"]:
            clicked()

    def timed_out():
        state["error"] = (
            "The GitHub download timed out. Check your connection and try again."
        )
        reply.abort()

    reply.connect("readyRead()", receive)
    reply.connect("downloadProgress(qint64,qint64)", progress)
    reply.connect("finished()", downloaded)
    button.connect("clicked()", clicked)
    dialog.connect("finished(int)", closed)
    timeout.connect("timeout()", timed_out)
    state["timeout"] = timeout
    _windows.append(state)
    dialog.show()
    timeout.start(60000)
    return state


def confirm_uninstall(data):
    import htls_installer as core
    from PythonQt import QtGui

    answer = QtGui.QMessageBox.question(
        None,
        "Uninstall HT Letterspacer",
        "Remove HT Letterspacer from the Scripts menu? Your fonts and their settings will be kept.",
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        QtGui.QMessageBox.No,
    )
    if answer != QtGui.QMessageBox.Yes:
        return
    try:
        for name in ("htls_fontlab.compact", "htls_fontlab.ui"):
            module = sys.modules.get(name)
            window = getattr(module, "_window", None)
            if window:
                window.dialog.close()
        backup = core.uninstall(data)
        refresh_scripts()
        QtGui.QMessageBox.information(
            None,
            "HT Letterspacer",
            "Uninstalled. A recoverable copy was kept at:\n" + backup,
        )
    except Exception as exc:
        QtGui.QMessageBox.warning(None, "HT Letterspacer", str(exc))

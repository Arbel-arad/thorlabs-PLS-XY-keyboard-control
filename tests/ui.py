from pynput.keyboard import Key, Listener
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import pynput
import time
import traceback
import sys
lastkey = "null"


def on_press(key):
    print('{0} pressed'.format(key))
    global lastkey
    lastkey = '{0}'.format(key)


def on_release(key):
    if key == Key.esc:
        return False    # Stop listener


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()  # Done


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.counter = 0
        self.l = QLabel("0")
        b = QPushButton("Start")
        b.pressed.connect(self.keyboard_listener)
        self.lastkey = QLabel("null")

        layout = QVBoxLayout()
        layout.addWidget(self.l)
        layout.addWidget(self.lastkey)
        layout.addWidget(b)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" %
              self.threadpool.maxThreadCount())

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.keyboard_listener()

    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def keyboard_listener_worker(self, progress_callback):
        with Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()
        return "listener stopped."

    def keyboard_listener(self):
        # Pass the function to execute
        # Any other args, kwargs are passed to the run function
        worker = Worker(self.keyboard_listener_worker)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        self.threadpool.start(worker)   # Execute

    def recurring_timer(self):
        global lastkey
        self.counter += 1
        self.l.setText("Counter: %d" % self.counter)
        self.lastkey.setText(lastkey)


app = QApplication([])
window = MainWindow()
app.exec()

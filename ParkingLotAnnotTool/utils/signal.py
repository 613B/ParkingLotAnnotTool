def qt_connect_signal_safely(signal, handler):
    signal.connect(handler)


def qt_disconnect_signal_safely(signal, handler=None):
    try:
        if handler is not None:
            while True:
                signal.disconnect(handler)
        else:
            signal.disconnect()
    except TypeError:
        pass
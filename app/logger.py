import logging


class Config():
    ''' Configures application wide settings and preferences '''

    @staticmethod
    def addLoggingLevel(name, intensity, method = None):
        if not method:
            method = name.lower()

        if hasattr(logging, name):
            raise AttributeError(f'{name} already defined in logging module')
        if hasattr(logging, method):
            raise AttributeError(f'{method} already defined in logging module')
        if hasattr(logging.getLoggerClass(), method):
            raise AttributeError(f'{method} already defined in logging class')

        def logForLevel(self, message, *args, **kwargs):
            if self.isEnabledFor(intensity):
                self._log(intensity, message, args, **kwargs)

        def logToRoot(message, *args, **kwargs):
            logging.log(intensity, message, *args, **kwargs)

        logging.addLevelName(intensity, name)

        setattr(logging, name, intensity)
        setattr(logging.getLoggerClass(), method, logForLevel)
        setattr(logging, method, logToRoot)

    @staticmethod
    def setLogger():
        Config.addLoggingLevel('TRACE', logging.DEBUG - 5)

        logger = logging.getLogger("sortipy")
        logger.propagate = False
        logger.setLevel("TRACE")

        console = logging.StreamHandler()
        console.setLevel("TRACE")
        console.setFormatter(CustomLogFormatter())

        logfile = logging.FileHandler(filename='/home/savant/Desktop/sortify/runtime.log')
        logfile.setLevel("TRACE")
        logfile.setFormatter(LogFileFormatter())

        logger.addHandler(console)
        logger.addHandler(logfile)

        return logger


class CustomLogFormatter(logging.Formatter):
    ''' Colorized Output for Log Terminal '''

    grey = "\033[38;2;154;154;154;20m"
    yellow = "\033[38;2;240;255;0;20m"
    green = "\033[38;2;0;255;0;20m"
    cyan = "\033[38;2;0;250;255;20m"
    red = "\033[38;2;255;0;0;20m"
    orange = "\033[38;2;255;155;0;20m"
    reset = "\033[38;2;0;255;0;20m"


    format_str = "[{levelname:^8}] {asctime} - {name:^16} - {message}"


    def format(self, record):
        _formats = {
            logging.TRACE: self.grey + self.format_str+ self.reset,
            logging.DEBUG: self.cyan + self.format_str + self.reset,
            logging.INFO: self.green + self.format_str + self.reset,
            logging.WARNING: self.yellow + self.format_str + self.reset,
            logging.ERROR: self.orange + self.format_str + self.reset,
            logging.FATAL: self.red + self.format_str + self.reset
        }

        log_fmt = _formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, style='{')

        return formatter.format(record)


class LogFileFormatter(logging.Formatter):
    ''' Custom Output for Log Files'''

    format_str = "[{levelname:^8}] {asctime} - {name:^16} - {message}"


    def format(self, record):
        _formats = {
            logging.TRACE: self.format_str,
            logging.DEBUG: self.format_str,
            logging.INFO: self.format_str,
            logging.WARNING: self.format_str,
            logging.ERROR: self.format_str,
            logging.FATAL: self.format_str
        }

        log_fmt = _formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt, style='{')

        return formatter.format(record)

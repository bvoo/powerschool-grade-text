import logging


def addLoggingLevel(levelName, levelNum, methodName=None):
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def log():
    addLoggingLevel('SUCCESS', logging.INFO - 3)
    class handler(logging.StreamHandler):
        colors = {
            logging.SUCCESS: '\033[1;32m',
            logging.DEBUG: '\033[38;5;134m',
            logging.INFO: '\033[36m',
            logging.WARNING: '\033[33m',
            logging.ERROR: '\033[31m',
            logging.CRITICAL: '\033[101m',
        }
        reset = '\033[0m'
        fmtr = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                                '%m-%d-%Y %H:%M:%S')

        def format(self, record):
            color = self.colors[record.levelno]
            log = self.fmtr.format(record)
            reset = self.reset
            return color + log + reset


    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)

    logger.addHandler(handler())
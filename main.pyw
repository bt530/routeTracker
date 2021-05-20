#!/usr/bin/env python
from UI import *
from LogReader import *

import logging
import logging.config
import yaml

with open('logging.yaml', 'r') as f:
    log_cfg = yaml.safe_load(f.read())
logging.config.dictConfig(log_cfg)


# noinspection PyBroadException
def main():
    try:
        my_ui = UserInterface(log_reader=LogReader())
        my_ui.main_loop()
    except Exception:
        logging.exception("Unhandled error occurred!")


if __name__ == '__main__':
    logging.getLogger('root')
    logging.debug('Starting up!')
    main()

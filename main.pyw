#!/usr/bin/env python
from UI import UserInterface
from LogReader import LogReader

import logging
import logging.config
import yaml

try:
    with open('logging.yaml', 'r') as f:
        log_cfg = yaml.safe_load(f.read())
    logging.config.dictConfig(log_cfg)
except FileNotFoundError:
    logging.basicConfig(filename="routeTracker.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level='DEBUG')


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

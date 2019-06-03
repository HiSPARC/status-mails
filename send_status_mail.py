import smtplib
import logging
import sys
from collections import Counter

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config import LOG_FILE
from read_wordpress_db import get_station_contacts


SMTP_SERVER = 'mail.nikhef.nl'
STATUS_URL = 'https://data.hisparc.nl/api/network/status/'


# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class SendStatusMails(object):

    def __init__(self, trigger_on_status='problem', message='', log_filename=LOG_FILE):
        self.trigger_on_status = trigger_on_status
        self.message = message
        self.log_filename = log_filename
        self.status_dict = {}
        self._setup_logging()

    def _setup_logging(self):
        self.logger = logging.getLogger('status_mails')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.log_filename)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_station_status(self):
        try:
            r = requests_retry_session().get(STATUS_URL)
        except Exception as exc:
            self.logger.error(f'Cannot load status JSON from server {exc}')
            self.status_dict = None
        else:
            for item in r.json():
                self.status_dict[int(item['number'])] = item['status']

    def validate_status(self):
        """verify that the station data status makes sense.

        If less that 5 stations up, assume status processing has failed

        """
        if self.status_dict is None:
            return False
        c = Counter(self.status_dict.values())
        if c['up'] > 5:
            self.logger.info(f'UP: {c["up"]}. DOWN: {c["down"]}. PROBLEM: {c["problem"]} UNKNOWN: {c["unknown"]}')
        else:
            self.logger.error(f'Only {c["up"]} stations reported up. Assuming problem with server. No mails sent.')
            return False
        return True

    def _send_mails(self, queue):
        """send a list of mails to SMTP_SERVER"""
        self.logger.info(f'Sending mails using {SMTP_SERVER}.')
        with smtplib.SMTP(SMTP_SERVER) as server:
            for to, msg in queue:
                server.sendmail('bhrhispa@nikhef.nl', to, msg)
                self.logger.debug(f'sending mail to: {to}')

    def send_status_mail(self):
        mail_queue = []
        for station_number, status in self.status_dict.items():
            if status == self.trigger_on_status:
                contact_list = self.contacts.get(station_number, None)
                if contact_list is None:
                    self.logger.warning(f'No contacts available for station {station_number}.')
                else:
                    for contact in contact_list:
                        self.logger.info(f'sending statusmail for station {station_number} to {contact}')
                        msg = self.message.format(rcpt=contact.email, name=contact.name,
                                                  station_number=station_number)
                        mail_queue.append((contact.email, msg))
        self._send_mails(mail_queue)

    def run(self):
        self.logger.debug('Reading contacts from Wordpress DB')
        self.contacts = get_station_contacts()

        self.logger.debug('Getting status from data.hisparc.nl')
        self.get_station_status()
        if not self.validate_status():
            return 1

        self.logger.info(f'Sending mails for status {self.trigger_on_status}:')
        self.send_status_mail()

        self.logger.info('Done.')
        return 0


if __name__ == '__main__':
    daily_message = open('daily_status_mail.txt').read()
    S = SendStatusMails(message=daily_message)
    sys.exit(S.run())

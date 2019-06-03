#!/usr/bin/env python3
import sys
from send_status_mail import SendStatusMails

message = open('down_status_mail.txt').read()
sm = SendStatusMails(trigger_on_status='down', message=message)
rc = sm.run()
sys.exit(rc)

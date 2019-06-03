#!/usr/bin/env python3
import sys
from send_status_mail import SendStatusMails

message = open('problem_status_mail.txt').read()
sm = SendStatusMails(trigger_on_status='problem', message=message)
rc = sm.run()
sys.exit(rc)

Script to send status mails to station contacts

This lives on neckar in `/srv/hisparc/status-mails`

This reads (station_id, contact) tuples from the WordPress DB
And queries data.hisparc.nl for station status. Mails are sent to contacts
for stations with a certain status. (Problem: daily, Down: weekly)


Enviroment (python>=3.6) `/srv/hisparc/hisparc_venv` see also `requirements.txt`

```/etc/cron.d/hisparc
MAILTO="beheer@hisparc.nl,pasopgeenspatiegebruikentussenontvangers@nikhef.nl,nogiemand@nikhef.nl"
# Stuur een mail naar alle stations die 'problem' als data-status hebben
# tijdstip 8:30am
30 8 * * * hisparc cd /srv/hisparc/status-mails/ && /srv/hisparc/hisparc_venv/bin/python problem_status_mail.py
# weekly offline message: Monday 8:28am
28 8 * * 1 hisparc cd /srv/hisparc/status-mails/ && /srv/hisparc/hisparc_venv/bin/python down_status_mail.py
# send stations contact summary to beheer@hisparc: Monday 8:02am
2 8 * * 1 hisparc cd /srv/hisparc/status-mails/ && /srv/hisparc/hisparc_venv/bin/python station_contact_list.py | /bin/mail -s "Weekly station contact info summary" beheer@hisparc.nl
```

Note to self, how to push to github from neckar (deep within Nikhef firewall):

On `login.nikhef.nl` ssh into neckar, forward port 9000 to github.com:22
```
ssh -R *:9000:github.com:22 hisparc@neckar
```

On neckar add git remote that points into the tunnel:
```
git remote add tunnel [git@localhost:9000]:HiSPARC/status-mails.git
git pull tunnel
...
git push tunnel
```
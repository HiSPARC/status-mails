Script to send status mails to station contacts

This lives on neckar in `/srv/hisparc/status-mails`

This reads (station_id, contact) tuples from the WordPress DB
And queries data.hisparc.nl for station status. Mails are sent to contacts
for stations with a certain status. (Problem: daily, Down: weekly)


Enviroment (python>=3.6) `/srv/hisparc/hisparc_venv` see also `requirements.txt`

```/etc/cron.d/hisparc
# Stuur een mail naar alle stations die 'problem' als data-status hebben
# tijdstip 8:30am
30 8 * * * hisparc cd /srv/hisparc/status-mails/ && /srv/hisparc/hisparc_venv/bin/python problem_status_mail.py
# weekly offline message: Monday 8:28am
28 8 * * 1 hisparc cd /srv/hisparc/status-mails/ && /srv/hisparc/hisparc_venv/bin/python down_status_mail.py
```

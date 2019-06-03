import re
from collections import namedtuple, defaultdict

import sqlalchemy as sa
import sqlalchemy.orm as orm

from .config import DB_USER, DB_PASSWORD

CONNECTION_STR = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@localhost/wp_hisparc?charset=utf8'

StationContact = namedtuple('StationContact', 'name, email')


def str_to_list_of_ints(s):
    numbers = re.findall('\d+', s)
    try:
        return [int(i) for i in numbers if int(i) > 0]
    except Exception as e:
        return []

# Wordpress tables definitions.
# https://github.com/ramen/wordpress-sqlalchemy
# Copyright (c) 2010 by Dave Benjamin.
# LICENSE: https://github.com/ramen/wordpress-sqlalchemy/blob/master/LICENSE
metadata = sa.MetaData()
usermeta_table = sa.Table('his_usermeta', metadata,
    sa.Column('umeta_id', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('user_id', sa.Integer(), primary_key=False, nullable=False),
    sa.Column('meta_key', sa.String(length=255), primary_key=False),
    sa.Column('meta_value', sa.Text(length=None), primary_key=False),
    sa.ForeignKeyConstraint(['user_id'], ['his_users.ID']),
)

users_table = sa.Table('his_users', metadata,
    sa.Column('ID', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('user_login', sa.String(length=60), primary_key=False, nullable=False),
    sa.Column('user_pass', sa.String(length=64), primary_key=False, nullable=False),
    sa.Column('user_nicename', sa.String(length=50), primary_key=False, nullable=False),
    sa.Column('user_email', sa.String(length=100), primary_key=False, nullable=False),
    sa.Column('user_url', sa.String(length=100), primary_key=False, nullable=False),
    sa.Column('user_registered', sa.DateTime(timezone=False), primary_key=False, nullable=False),
    sa.Column('user_activation_key', sa.String(length=60), primary_key=False, nullable=False),
    sa.Column('user_status', sa.Integer(), primary_key=False, nullable=False),
    sa.Column('display_name', sa.String(length=250), primary_key=False, nullable=False),
)


# classes match the wordpress tables
class User(object):
    def __init__(self, user_login):
        self.user_login = user_login

    def __repr__(self):
        return '<User(%r)>' % self.user_login


class UserMeta(object):
    def __init__(self, meta_key, meta_value):
        self.meta_key = meta_key
        self.meta_value = meta_value

    def __repr__(self):
        return '<UserMeta(%r, %r)>' % (self.meta_key, self.meta_value)


orm.mapper(UserMeta, usermeta_table)
orm.mapper(User, users_table)


def connect(db_str=CONNECTION_STR):
    """Setup a connection to the wordpress DB engine"""
    engine = sa.create_engine(db_str)
    session = sa.orm.sessionmaker(engine)()
    return session


def get_station_contacts(session=connect()):
    """Query the wordpress DB for station contacts

    A wordpress user which has an 'is_admin' record in the usermeta table
    assiociated with its user ID is considered to be a station contact.

    The station number is stored in a seperate 'station_id' record in the
    usermeta table.

    `station_id` is an ascii string with comma seperated station numbers.
    """
    query = session.query(UserMeta).filter((UserMeta.meta_key == 'is_admin'))
    contacts = defaultdict(list)
    for row in query:
        is_admin = row.meta_value
        user_id = row.user_id
        u = session.query(User).filter(User.ID == user_id).first()
        if 'yes' not in is_admin:
            continue
        meta_record = session.query(UserMeta).filter((UserMeta.user_id == user_id) & (UserMeta.meta_key == 'station_id')).first()
        for sn in str_to_list_of_ints(meta_record.meta_value):
            u = session.query(User).filter(User.ID == user_id).first()
            # print(f'User: {u.user_nicename} email: {u.user_email} station: {sn}')
            contacts[int(sn)].append(StationContact(u.display_name, u.user_email))
    return contacts


if __name__ == '__main__':
    contacts = get_station_contacts()
    for sn, users in contacts.items():
        for user in users:
            print(f'User: {user.name} email: {user.email} station: {sn}')

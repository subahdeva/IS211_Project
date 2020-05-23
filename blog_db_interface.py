#!/usr/bin/env python
# coding: utf-8


import os
import sqlite3
from contextlib import closing


class DBInterface(object):
    def __init__(self, app):
        self.table = ''
        if not os.path.exists(app.config['DATABASE']):
            self.db_init(app)

    def db_connect(self, app):
        if app.config['DATABASE'] is not None:
            conn = sqlite3.connect(app.config['DATABASE'])
            conn.row_factory = sqlite3.Row
            return conn
        return False

    def db_init(self, app):
        with closing(self.db_connect(app)) as db:
            with app.open_resource(
                    app.config['DDL'],
                    mode='r') as schema:
                db.cursor().executescript(schema.read())
                db.commit()

    def getdata(self, conn, query):
        with closing(conn) as db:
            db.row_factory = sqlite3.Row
            cur = db.cursor()
            res = cur.execute(query).fetchall()
            return res

    def insert(self, conn, table, fields=(), values=()):
        self.table = table
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            self.table, ', '.join(fields),
            ', '.join(['?'] * len(values)))
        cur = conn.execute(query, values)
        conn.commit()
        stat = cur.lastrowid
        cur.close()
        return stat

    def update(self, conn, table, index, fields, values):
        self.table = table
        query = 'UPDATE {} SET '.format(self.table)
        query += ', '.join([' = '.join(items)
                            for items in zip(fields,
                                             '?' * len(values))])
        query += ' WHERE {} = {}'.format(index.get('field'),
                                           index.get('value'))

        cur = conn.cursor()
        cur.execute(query, values)
        stat = conn.commit()
        cur.close()
        return stat

    def delete(self, conn, table, fields=(), values=(), operator=None):
        self.table = table
        query = 'DELETE FROM ' + self.table

        if len(fields) > 0 and len(fields) == len(values):
            cond = ' WHERE '
            if operator is not None:
                cond += operator.join(
                    [' = '.join(items) for items in
                     zip(fields, '?' * len(values))])
            else:
                cond += ' = '.join([str(fields[0]), '?' * len(values)])
            query += cond
        cur = conn.cursor()
        cur.execute(query, values)
        stat = conn.commit()
        cur.close()
        return stat


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Steven'

import pymysql
import logging

OperationalError = pymysql.OperationalError


class MySQL:
    def __init__(self, host, user, password, db, port=3306, charset="utf8"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset
        self.db = db
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password)
            self.conn.autocommit(False)
            self.conn.set_charset(self.charset)
            self.cur = self.conn.cursor()
            self.conn.select_db(self.db)
        except pymysql.Error as e:
            logging.exception("Mysql Error %d: %s" % (e.args[0], e.args[1]))

    def __del__(self):
        self.close()

    def selectDb(self, db):
        try:
            self.conn.select_db(db)
        except pymysql.Error as e:
            logging.exception("Mysql Error %d: %s" % (e.args[0], e.args[1]))

    def query(self, sql):
        try:
            n = self.cur.execute(sql)
            return n
        except pymysql.Error as e:
            logging.exception("Mysql Error:%s\nSQL:%s" % (e, sql))

    def fetchRow(self):
        result = self.cur.fetchone()
        return result

    def fetchAll(self):
        result = self.cur.fetchall()
        desc = self.cur.description
        d = []
        for inv in result:
            _d = {}
            for i in range(0, len(inv)):
                _d[desc[i][0]] = str(inv[i])
            d.append(_d)
        return d

    def insert(self, table_name, data):
        columns = data.keys()
        _prefix = "".join(['INSERT INTO `', table_name, '`'])
        _fields = ",".join(["".join(['`', column, '`']) for column in columns])
        _values = ",".join(["%s" for i in range(len(columns))])
        _sql = "".join([_prefix, "(", _fields, ") VALUES (", _values, ")"])
        _params = [data[key] for key in columns]
        return self.cur.execute(_sql, tuple(_params))

    def update(self, tbname, data, condition):
        if len(data) == 0:
            return
        _fields = []
        _prefix = "".join(['UPDATE `', tbname, '` ', 'SET'])
        for key in data.keys():
            _fields.append("%s = '%s" % (key, data[key]) + "'")
        fieldstr = ", ".join(_fields)
        _sql = " ".join([_prefix, fieldstr, "WHERE", condition])
        logging.debug(_sql)

        return self.cur.execute(_sql)

    def delete(self, tbname, condition):
        _prefix = "".join(['DELETE FROM  `', tbname, '`', 'WHERE'])
        _sql = "".join([_prefix, condition])
        return self.cur.execute(_sql)

    def getLastInsertId(self):
        return self.cur.lastrowid

    def rowcount(self):
        return self.cur.rowcount

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    my = MySQL('127.0.0.1', 'root', 'alibaba', 'gtjdb', 3306)
    # tbname = 'gtj_railway'
    # data = {'railway_name': '古島', 'railway_type': '跨座式モノレール', 'operation_company': '沖縄都市モノレール',
    #         'service_provider_type': '第三セクター'}
    # my.insert(tbname, data)
    # my.commit()
    count = my.query("select id from gtj_railway where railway_name='いわて銀河鉄道線'")
    if count == 1:
        railway_id = my.fetchRow()[0]
        print(railway_id)

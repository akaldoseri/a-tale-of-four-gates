import os

import mysql.connector
import pprint


class DatabaseInterface:

    def __init__(self):
        self.endpoint = "cp55.ckxgs3folg2a.eu-west-1.rds.amazonaws.com"
        self.port = "3306"
        self.user = "admin"
        self.passwd = os.getenv("CP55PASSWD")
        self.db_name = "cp55"

    def get_connection(self):
        if self.passwd is None:
            return None

        try:
            conn = mysql.connector.connect(host=self.endpoint, user=self.user, passwd=self.passwd,
                                           port=self.port, database=self.db_name)
            return conn
        except Exception as e:
            print("Database connection failed due to {}".format(e))

    def insert_app(self, package_name, analysis_status):
        query = "INSERT INTO apps (package_name, analysis_status) VALUES (%s, %s);"
        values = (package_name, analysis_status)

        conn = self.get_connection()
        if conn is None:
            pprint.pp("App: " + package_name + ". analysis status: " + analysis_status)
            return

        cursor = conn.cursor()
        cursor.execute(query, values)

        conn.commit()

        return cursor.lastrowid

    def insert_components(self, app_id, components):
        for component in components:
            component["app_id"] = app_id

        query = "INSERT INTO components (app_id, name, type, enabled, exported, direct_boot_aware, filter_matches, " \
                "permission, authorities, grant_uri_permission, write_permission, read_permission, has_sql, " \
                "foreground_service_type) " \
                "VALUES (%(app_id)s, %(name)s, %(type)s, %(enabled)s, %(exported)s, %(direct_boot_aware)s, " \
                "%(filter_matches)s, %(permission)s, %(authorities)s, %(grant_uri_permission)s, " \
                "%(write_permission)s, %(read_permission)s, %(has_sql)s, %(foreground_service_type)s);"

        conn = self.get_connection()
        if conn is None:
            pprint.pp(components)
            return

        cursor = conn.cursor()
        cursor.executemany(query, components)

        conn.commit()

        return cursor.lastrowid

    def insert_sql_checks(self, app_id, sql_checks):
        for sql_check in sql_checks:
            sql_check["app_id"] = app_id

        query = "INSERT INTO sql_checks (app_id, provider_name, method_name, has_query_checks, has_uri_checks)" \
                "VALUES (%(app_id)s, %(provider_name)s, %(method_name)s, %(has_query_checks)s, %(has_uri_checks)s);"

        conn = self.get_connection()
        if conn is None:
            pprint.pp(sql_checks)
            return

        cursor = conn.cursor()
        cursor.executemany(query, sql_checks)

        conn.commit()

        return cursor.lastrowid

    def update_app_analysis_status(self, app_id, status):
        query = "UPDATE apps SET analysis_status = %s WHERE id = %s;"
        values = (status, app_id)

        conn = self.get_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(query, values)

        conn.commit()

        return cursor.lastrowid

    def get_app_id_by_package_name(self, package_name):
        query = "SELECT id FROM apps WHERE package_name = %s;"

        conn = self.get_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(query, (package_name,))

        app_id = cursor.fetchone()

        return app_id[0]

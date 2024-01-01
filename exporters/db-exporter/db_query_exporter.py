import os
import time
import logging

import pymysql

from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge

# load environment variables from .env file
load_dotenv()

# MySQL connection parameters
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASS = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DATABASE')

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Custom exporter class
class CustomExporter:
    def __init__(self, name, query):
        self.name = name
        self.query = query
        self.metric_dict = {}

    # Run the query and return the result
    def run_query(self) -> None:
        # Connect to MySQL
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            passwd=MYSQL_PASS,
            db=MYSQL_DB
        )
        # Create cursor to execute query
        try:
            with conn.cursor() as cursor:
                cursor.execute(self.query)
                # result = cursor.fetchall()
                # return result
                return
        except Exception as e:
            print(f'Error: {e}')
        finally:
            conn.close()

    def create_metric(self, metric_name) -> None:
        if self.metric_dict.get(metric_name) is None:
            self.metric_dict[metric_name] = Gauge(metric_name.lower(), f'{self.name} query duration',
                                                  labelnames=['query'])

    def update_metric(self, metric_name) -> None:
        start_time = time.time()
        self.run_query()
        duration = time.time() - start_time
        logging.info(f'Query execution took {duration} seconds')
        self.metric_dict[metric_name].labels(query=self.query).set(duration)

    def main(self):
        metric_name = f'cust_{self.name}_query_duration'
        duration = int(os.environ.get('DURATION', 10))
        exporter_port = int(os.environ.get('EXPORTER_PORT', 9105))
        start_http_server(exporter_port)
        while True:
            self.create_metric(metric_name)
            self.update_metric(metric_name)
            time.sleep(duration)


if __name__ == "__main__":
    # Create a CustomExporter object
    query = 'SELECT * FROM employees'
    exporter = CustomExporter('MySQL', query)
    exporter.main()

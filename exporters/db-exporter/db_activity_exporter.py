"""Custom exporter for DB metrics."""

import os
import time
import logging
import psycopg2

from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Enum

# Load environment variables
load_dotenv()

# Load DB connection parameters
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DATABASE')

# Set logging level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

class DBMetrics:
    """
    Class for DB metrics.
    """

    def __init__(self, polling_interval_seconds=5, max_connection=5):
        self.polling_interval_seconds = polling_interval_seconds
        self.max_connection = max_connection
        self.db_connection = None

        # Define metrics to collect
        self.db_host_status = Enum(
            'db_host_status',
            'Status of db host',
            states=['up', 'down']
        )
        self.db_idle_connections = Gauge(
            'db_idle_connections',
            'Number of idle db connections',
            ['db_name', 'db_host', 'db_port']
        )

    def run_metrics_loop(self):
        """
        Run metrics loop.
        """

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from db and refresh prometheus metrics with new values.
        """

        try:
            # Connect to db if not connected
            if self.db_connection is None:
                self.db_connection = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )
                # set db host status to up
                self.db_host_status.state('up')

            # Get active connections
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'idle';")
                idle_connections = cursor.fetchone()[0]
                # set metric value
                labels = {'db_name': DB_NAME, 'db_host': DB_HOST, 'db_port': DB_PORT}
                self.db_idle_connections.labels(**labels).set(idle_connections)
                samples = self.db_idle_connections.collect()
                current_value = samples[0].samples[0].value
                logging.info(f'Idle connections: {current_value}')
        except psycopg2.OperationalError as error:
            # set db host status to down
            self.db_host_status.state('down')
            logging.error(f'Error connecting to db {DB_NAME}: {error}')
        except psycopg2.InterfaceError:
            # set db host status to down
            self.db_host_status.state('down')
            logging.debug(f'DEBUG: Database connection is closed')
        except Exception as e:
            logging.error(f'Error getting idle connections: {e}')
        finally:
            # Close the cursor and connection
            if self.db_connection is not None or 'cursor' in locals():
                cursor.close()
                self.db_connection = None


def main():
    """
    Main entry point.
    """

    polling_interval_seconds = int(os.environ.get('POLLING_INTERVAL_SECONDS', 5))
    max_connection = int(os.environ.get('MAX_CONNECTION', 5))
    exporter_port = int(os.environ.get('EXPORTER_PORT', 9110))

    db_metrics = DBMetrics(polling_interval_seconds, max_connection)
    start_http_server(exporter_port)
    db_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()

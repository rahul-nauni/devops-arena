import os
import logging
import argparse
from time import sleep
from glob import glob

from prometheus_client import start_http_server, Gauge

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setting up the argument parser
parser = argparse.ArgumentParser()

# Required args
parser.add_argument('-d', '--dir', required=True, help='Directory to watch')
parser.add_argument('-e', '--ext', required=True, help='Extension to watch')
args = parser.parse_args()


class CustomExporter:
    def __init__(self, dir: str, ext: str) -> None:
        self.dir = dir
        self.ext = ext
        self.metric_dict = {}

    def count_files_in_dir(self) -> int:
        """
        DOCSTRING: Counts the number of files in a directory with a specific extension
        INPUT: dir:str, ext:str
        OUTPUT: number (int)
        """
        file_list = [f for f in glob(os.path.join(self.dir, f'*.{self.ext}'))]
        logging.info(f'Found {len(file_list)} files with extension {self.ext} in {self.dir}')
        return len(file_list)

    def create_metric(self, metric_name) -> None:
        if self.metric_dict.get(metric_name) is None:
            self.metric_dict[metric_name] = Gauge(metric_name, f'Number of *{self.ext} files in {self.dir}')

    def update_metric(self, metric_name) -> None:
        self.metric_dict[metric_name].set(self.count_files_in_dir())

    def main(self):
        metric_name = f'cust_{self.ext}_files_in_{self.dir.replace("/", "_")}_total'
        duration = int(os.environ.get('DURATION', 5))
        exporter_port = int(os.environ.get('EXPORTER_PORT', 9104))
        start_http_server(exporter_port)
        while True:
            self.create_metric(metric_name)
            self.update_metric(metric_name)
            sleep(duration)


if __name__ == "__main__":
    dir, ext = args.dir, args.ext
    exporter = CustomExporter(dir, ext)
    exporter.main()

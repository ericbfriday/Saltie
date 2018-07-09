import gzip
import io

from examples.legacy.legacy_input_formatter import LegacyInputFormatter
from examples.legacy.legacy_output_formatter import LegacyOutputFormatter
from examples.multi_output_model import MultiOutputKerasModel
from framework.model_holder.base_model_holder import BaseModelHolder
from examples.lstm.example_lstm_model import ExampleLSTMModel
from examples.example_model_holder import ExampleModelHolder
from examples.lstm.lstm_input_formatter import LSTMInputFormatter
from examples.lstm.lstm_output_formatter import LSTMOutputFormatter
from trainer.base_trainer import BaseTrainer
from trainer.downloader import Downloader
import trainer.binary_converter as bc


class DownloadTrainer(BaseTrainer):
    def __init__(self, model_holder: BaseModelHolder):
        super().__init__(model_holder)
        self.downloader = Downloader()

    def train_on_file(self):
        input_file = self.downloader.get_random_replay()
        file_name = input_file[1]
        input_file = input_file[0]
        if isinstance(input_file, io.BytesIO):
            input_file.seek(0)
            with gzip.GzipFile(fileobj=input_file, mode='rb') as f:
                bc.read_data(f, self.model_holder.process_pair, batching=True)

    def train_on_files(self):
        input_file_list = self.downloader.get_replays(1000)
        counter = 0
        for input_file in input_file_list:
            file_name = input_file[1]
            input_file = input_file[0]
            if isinstance(input_file, io.BytesIO):
                input_file.seek(0)
                with gzip.GzipFile(fileobj=input_file, mode='rb') as f:
                    bc.read_data(f, self.model_holder.process_pair, batching=True)
            counter += 1
            if counter % 10 == 0:
                print('FILE', counter)

    def finish(self):
        self.model_holder.finish_training()


if __name__ == '__main__':
    d = DownloadTrainer(ExampleModelHolder(MultiOutputKerasModel(ExampleLSTMModel()),
                                           LSTMInputFormatter(LegacyInputFormatter()),
                                           LSTMOutputFormatter(LegacyOutputFormatter())))
    d.train_on_files()
    d.finish()

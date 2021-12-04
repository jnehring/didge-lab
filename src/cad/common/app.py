import configargparse
import logging

class App:

    config=None
    context={}

    @classmethod
    def init_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - {%(filename)s:%(lineno)d} - %(levelname)s: %(message)s')

    @classmethod
    def get_config(cls, path="config.ini"):
        if App.config==None:
            p = configargparse.ArgParser(default_config_files=['./*.conf'])
            p.add('-no_cache', action='store_true', help='disable pipeline caching. default=False')
            p.add('-n_threads', type=int, default=20, help='number of threads')
            p.add('-n_poolsize', type=int, default=10, help='pool size')
            p.add('-n_generations', type=int, default=1000, help='number of generations')
            p.add('-n_generation_size', type=int, default=30, help='generation size')
            p.add('-pipelines_dir', type=str, default="projects/pipelines/", help='project directory')
            options = p.parse_args()

            App.config=options

            # add config to context
        return App.config
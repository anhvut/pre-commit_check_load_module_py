import argparse
import contextlib
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import List

IS_WINDOWS = sys.platform == 'win32'

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s')
logging.root.setLevel(logging.INFO)


@contextlib.contextmanager
def temporary_filename(suffix=None):
    """Context that introduces a temporary file.

    Creates a temporary file, yields its name, and upon context exit, deletes it.
    (In contrast, tempfile.NamedTemporaryFile() provides a 'file' object and
    deletes the file as soon as that file object is closed, so the temporary file
    cannot be safely re-opened by another library or process.)

    Args:
      suffix: desired filename extension (e.g. '.mp4').

    Yields:
      The name of the temporary file.

    Note: courtesy of https://stackoverflow.com/a/57701186/19555840
    """
    import tempfile

    tmp_name = None
    try:
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp_name = f.name
        f.close()
        yield tmp_name
    finally:
        os.unlink(tmp_name)


@dataclass()
class ConfigPrefix:
    prefix: str
    interpreter: str
    pythonpath: str


@dataclass()
class Config:
    prefixes: List[ConfigPrefix]
    filenames: List[str]


def init_config(argv):
    import configparser
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to run')
    parser.add_argument('--config', '-c', action='store_true', dest='config_file', default='.check_load_module', help='Configuration file')
    args = parser.parse_args(argv)

    result = Config([], args.filenames)

    if args.config_file and os.path.isfile(args.config_file):
        config = configparser.ConfigParser()
        config.read(args.config_file)
        if logfile := config.get('DEFAULT', 'logfile', fallback='').strip():
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
            root_logger = logging.getLogger()
            if not [x for x in root_logger.handlers if isinstance(x, logging.FileHandler) and x.baseFilename == logfile]:
                root_logger.addHandler(file_handler)
        for section in config.sections():
            pythonpath = config.get(section, 'PYTHONPATH', fallback='')
            if IS_WINDOWS:
                pythonpath = pythonpath.replace(':', ';')
            else:
                pythonpath = pythonpath.replace(';', ':')
            result.prefixes.append(ConfigPrefix(
                config.get(section, 'prefix', fallback=''),
                config.get(section, 'interpreter', fallback=sys.executable),
                pythonpath
            ))
    else:
        logging.info('No config file found, using default')
        result.prefixes.append(ConfigPrefix('', sys.executable, ''))
    logging.info(f'Running {sys.executable} in {os.getcwd()} - argv = {argv}')
    return result


def main(argv=None):
    config = init_config(argv)
    filenamesByPrefix = {}
    for filename in config.filenames:
        prefix = None
        for config_prefix in config.prefixes:
            if filename.startswith(config_prefix.prefix):
                prefix = config_prefix.prefix
                break
        if prefix is not None:
            if (entry := filenamesByPrefix.get(prefix)) is None:
                filenamesByPrefix[prefix] = entry = []
            entry.append(filename)
        else:
            logging.info(f'File {filename} do not match any prefix, ignored')

    for [prefix, filenames] in filenamesByPrefix.items():
        logging.info(f'Checking {len(filenames)} files with prefix {prefix or "(none)"}')

        config_prefix = next(x for x in config.prefixes if x.prefix == prefix)
        with temporary_filename('.py') as generated_script_filename:
            with open(generated_script_filename, 'wt') as f:
                f.write("""
def dynamic_load(python_file_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('check_load', python_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module \n\n\n""")
                escaped_filenames = [f'"{f}"' for f in filenames]
                f.write(f'\n\nfor f in [{",".join(escaped_filenames)}]:\n')
                f.write('    print("Checking " + f)\n')
                f.write('    dynamic_load(f)\n')

            ret = subprocess.run([config_prefix.interpreter, generated_script_filename], env=os.environ | {'PYTHONPATH': config_prefix.pythonpath})
            logging.info(f'ret = {ret}')
            if ret.returncode != 0:
                return ret.returncode

    return 0


if __name__ == '__main__':
    exit(main())

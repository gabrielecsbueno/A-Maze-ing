from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    '''
    Dataclass that holds all configuration values parsed from config.txt.
    '''
    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool = False
    seed: Optional[str] = None


def parse_config(arq_config: str) -> Config:
    '''
    The parse_config function reads the 'config.txt' file, validates the
    presence of the required keys, and returns a 'dataclass Config'
    '''
    info_config = {}
    try:
        with open(arq_config, 'r') as file_r:
            for line in file_r.readlines():
                if not line.strip() or line.startswith('#'):
                    continue
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    if parts[0] in info_config:
                        raise ValueError(f"key '{parts[0]}' in "
                                         "'config.txt' is duplicated.")
                    info_config[parts[0]] = parts[1]
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Error: config file not found: {err}")
    if not info_config:
        raise ValueError("Error: file 'config.txt' is empty!!")

    required_keys = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE',
                     'PERFECT']

    validation_missing = [x for x in required_keys if x not in info_config]

    if validation_missing:
        raise ValueError("Error: missing keys in 'config.txt'")

    try:
        width = int(info_config['WIDTH'])
        height = int(info_config['HEIGHT'])

        split_entry = info_config['ENTRY'].split(',', 1)
        entry: tuple[int, int] = (int(split_entry[0]), int(split_entry[1]))

        split_exit = info_config['EXIT'].split(',', 1)
        exit_: tuple[int, int] = (int(split_exit[0]), int(split_exit[1]))

        output_file = info_config['OUTPUT_FILE'].strip()
        if not output_file:
            raise ValueError("Error: OUTPUT_FILE cannot be empty")

        perfect_raw = info_config['PERFECT'].strip().lower()
        if perfect_raw not in ('true', 'false'):
            raise ValueError(
                f"Error: PERFECT must be 'True' or 'False',"
                f" got '{info_config['PERFECT']}'"
            )
        perfect = perfect_raw == 'true'

        seed_raw = info_config.get('SEED', None)
        seed = seed_raw.strip() if seed_raw is not None else None
        if seed == '':
            raise ValueError("Error: SEED cannot be empty")

    except Exception as err:
        raise Exception(f"Error: invalid value - {err}")

    return Config(width=width, height=height, entry=entry, exit_=exit_,
                  output_file=output_file, perfect=perfect, seed=seed)

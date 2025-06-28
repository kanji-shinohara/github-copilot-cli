import yaml

from github_copilot_cli.lib.logger import logger

encoding_format_utf_8 = "utf-8"


def load_and_validate_config_file(category: str, config_file_path: str) -> dict:
    try:
        with open(config_file_path, "r", encoding=encoding_format_utf_8) as f:
            config_file = yaml.safe_load(f)
            config = config_file.get(category, {})
            return config
    except FileNotFoundError as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}] -- {error}"
        )
    except yaml.YAMLError as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}] -- {error}"
        )
    except UnicodeDecodeError as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}] -- {error}"
        )
    except Exception as error:
        logger.error(
            f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}] -- {error}"
        )
    return {}

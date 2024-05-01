from pathlib import Path
from typing import Final


# NOTE: In conformance with PEP517, versions should be stored as:
# `__version__ = 'a.b.c'` (e.g., no f-string)
# In order to dynamically set the version string, we use this script
# to write the version declaration to `version.py`.
VERSION: Final[str] = "0.0.1"
DISCLAIMER: Final[
    str
] = "# This file is auto-generated by `create_version_file.py`.\n# It is not intended for manual editing."
VERSION_PATH: Final[Path] = Path.cwd() / "lzss" / "version.py"
ALPHA_INDICATOR: Final[str] = "a"


def get_version_modifier() -> str:
    # This function increments the alpha number: 1.0.0 -> 1.0.0a0 -> 1.0.0a1 ...
    # Attempt to overwrite `__version__`
    if VERSION_PATH.is_file():
        exec_result = {}
        exec(open(VERSION_PATH).read(), exec_result)
        __version__ = exec_result["__version__"]

        version_without_modifier = __version__.split(ALPHA_INDICATOR)[0]
        if version_without_modifier == VERSION:
            if ALPHA_INDICATOR in __version__:
                alpha_number = 1 + int(__version__.split(ALPHA_INDICATOR)[-1])
                return f"{ALPHA_INDICATOR}{alpha_number}"
            else:
                return f"{ALPHA_INDICATOR}0"

    return ""


def main():
    version_string = f"{VERSION}{get_version_modifier()}"
    with open(VERSION_PATH, "w") as f:
        f.write(f'{DISCLAIMER}\n__version__ = "{version_string}"\n')


if __name__ == "__main__":
    main()
# TFD Search Tool

This is a command-line tool for searching and exporting data about weapons and modules from the game TFD (The First Descendant). The data is pulled from the Nexon open API and cached locally for faster access.

## Features

- Search for weapons and modules by name
- Display detailed information about weapons and modules
- Export weapon and module data to CSV files

## Data Sources

The data is pulled from the following URLs:

- **Weapons**: [Weapon Data](https://open.api.nexon.com/static/tfd/meta/en/weapon.json)
- **Stats**: [Stat Data](https://open.api.nexon.com/static/tfd/meta/en/stat.json)
- **Modules**: [Module Data](https://open.api.nexon.com/static/tfd/meta/en/module.json)

### Setup

```sh
git clone https://github.com/http-kennedy/dev_tfd_search
cd dev_tfd_search
pip install -r requirements.txt
```

### Use

```sh
python src/dev-tfd-search/tfd_search.py
```

### For Windows Users

You can download the pre-built executable from the repository:

[Download tfd_search.exe](https://github.com/http-kennedy/dev_tfd_search/blob/main/windows_executable/tfd_search.exe)

--------------------------------

1. **Search Weapons**: Search for a weapon by name and display detailed information.
2. **Search Modules**: Search for a module by name and display detailed information.
3. **Refresh Cache**: Refresh the local cache by fetching the latest data from the API. (Does not refresh automatically)
4. **Export to CSV**: Export the displayed information to a CSV file.

## Cache Location

The data is cached locally to improve performance. The cache files are stored in the following locations depending on your operating system:

- **Windows**: `C:\Users\<YourUserName>\AppData\Local\dev_tfd_search`
- **Linux/macOS**: `/home/<YourUserName>/.config/dev_tfd_search`

## Requirements

- Python 3.6+
- `questionary` library
- `requests` library
- `rich` library

## Notes

- This tool was quickly made to format the data easier. -> **EXPECT BUGS** <-
- If you encounter any issues, please report them in the issue tracker.

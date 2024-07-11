import csv
import json
import os
import platform
from typing import Any, Dict, List, Optional

import questionary
import requests
from rich.columns import Columns
from rich.console import Console
from rich.table import Table

console = Console()


def get_cache_dir() -> str:
    if platform.system() == "Windows":
        return os.path.join(os.getenv("LOCALAPPDATA"), "dev_tfd_search")
    return os.path.join(os.path.expanduser("~"), ".config", "dev_tfd_search")


CACHE_DIR = get_cache_dir()
CACHE_FILE = os.path.join(CACHE_DIR, "weapon.json")
STAT_CACHE_FILE = os.path.join(CACHE_DIR, "stat.json")
MODULE_CACHE_FILE = os.path.join(CACHE_DIR, "module.json")
WEAPON_JSON_URL = "https://open.api.nexon.com/static/tfd/meta/en/weapon.json"
STAT_JSON_URL = "https://open.api.nexon.com/static/tfd/meta/en/stat.json"
MODULE_JSON_URL = "https://open.api.nexon.com/static/tfd/meta/en/module.json"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def fetch_and_cache_json(url: str, cache_file: str) -> List[Dict[str, Any]]:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w") as file:
        json.dump(data, file)

    return data


def load_json_from_cache(cache_file: str) -> List[Dict[str, Any]]:
    with open(cache_file, "r") as file:
        return json.load(file)


def load_weapon_data() -> List[Dict[str, Any]]:
    if not os.path.exists(CACHE_FILE):
        return fetch_and_cache_json(WEAPON_JSON_URL, CACHE_FILE)
    return load_json_from_cache(CACHE_FILE)


def load_stat_data() -> Dict[str, str]:
    if not os.path.exists(STAT_CACHE_FILE):
        data = fetch_and_cache_json(STAT_JSON_URL, STAT_CACHE_FILE)
    else:
        data = load_json_from_cache(STAT_CACHE_FILE)

    return {item["stat_id"]: item["stat_name"] for item in data}


def load_module_data() -> List[Dict[str, Any]]:
    if not os.path.exists(MODULE_CACHE_FILE):
        return fetch_and_cache_json(MODULE_JSON_URL, MODULE_CACHE_FILE)
    return load_json_from_cache(MODULE_CACHE_FILE)


def refresh_cache() -> None:
    print("Refreshing cache...")
    fetch_and_cache_json(WEAPON_JSON_URL, CACHE_FILE)
    fetch_and_cache_json(STAT_JSON_URL, STAT_CACHE_FILE)
    fetch_and_cache_json(MODULE_JSON_URL, MODULE_CACHE_FILE)
    print("Cache refreshed.\n")
    questionary.text("Press enter to return to main menu").ask()


def search_items(
    items: List[Dict[str, Any]], search_term: str, key: str
) -> List[Dict[str, Any]]:
    return [item for item in items if search_term.lower() in item[key].lower()]


def create_base_stats_table(weapon: Dict[str, Any], stat_map: Dict[str, str]) -> Table:
    base_stats_table = Table(title=f"{weapon['weapon_name']} - Base Stats")

    base_stats_table.add_column("Attribute", style="bold")
    base_stats_table.add_column("Value", style="bold")

    base_stats_table.add_row("Weapon ID", weapon["weapon_id"])
    base_stats_table.add_row("Weapon Type", weapon["weapon_type"])
    base_stats_table.add_row("Weapon Tier", weapon["weapon_tier"])
    base_stats_table.add_row("Rounds Type", weapon["weapon_rounds_type"])

    for stat in weapon["base_stat"]:
        stat_name = stat_map.get(stat["stat_id"], f"Unknown Stat ({stat['stat_id']})")
        base_stats_table.add_row(stat_name, str(stat["stat_value"]))

    return base_stats_table


def create_firearm_attack_table(
    weapon: Dict[str, Any], stat_map: Dict[str, str], start_level: int, end_level: int
) -> Table:
    firearm_attack_table = Table(
        title=f"{weapon['weapon_name']} - Firearm Attack ({start_level}-{end_level})"
    )

    firearm_attack_table.add_column("Level", style="bold")
    firearm_attack_table.add_column("Type", style="bold")
    firearm_attack_table.add_column("Value", style="bold")

    for level_info in weapon["firearm_atk"]:
        level = level_info["level"]
        if start_level <= level <= end_level:
            for firearm in level_info["firearm"]:
                stat_name = stat_map.get(
                    firearm["firearm_atk_type"],
                    f"Unknown Stat ({firearm['firearm_atk_type']})",
                )
                firearm_attack_table.add_row(
                    str(level), stat_name, str(firearm["firearm_atk_value"])
                )

    return firearm_attack_table


def create_module_stats_table(module: Dict[str, Any]) -> Table:
    module_stats_table = Table(title=f"{module['module_name']} - Stats")

    module_stats_table.add_column("Level", style="bold")
    module_stats_table.add_column("Capacity", style="bold")
    module_stats_table.add_column("Value", style="bold")

    for stat in module["module_stat"]:
        module_stats_table.add_row(
            str(stat["level"]), str(stat["module_capacity"]), stat["value"]
        )
        module_stats_table.add_row("", "", "")

    return module_stats_table


def display_weapon_info(weapon: Dict[str, Any], stat_map: Dict[str, str]) -> None:
    attack_ranges = [(1, 30), (31, 60), (61, 90), (91, 120), (121, 160)]
    options = [f"{start}-{end}" for start, end in attack_ranges]

    choice = questionary.select(
        "Choose the range of firearm attack levels to display:",
        choices=options + ["Back"],
        default="91-120",
    ).ask()

    if choice is None or choice == "Back":
        return

    start, end = map(int, choice.split("-"))
    base_stats_table = create_base_stats_table(weapon, stat_map)
    firearm_attack_table = create_firearm_attack_table(weapon, stat_map, start, end)

    columns = Columns([base_stats_table, firearm_attack_table])
    console.print(columns)

    next_action = questionary.select(
        "What would you like to do next?",
        choices=["Return to main menu", "Output to CSV"],
        default="Return to main menu",
    ).ask()

    if next_action == "Output to CSV":
        export_json_to_csv(weapon, stat_map)


def display_module_info(module: Dict[str, Any]) -> None:
    module_stats_table = create_module_stats_table(module)
    console.print(module_stats_table)

    next_action = questionary.select(
        "What would you like to do next?",
        choices=["Return to main menu", "Output to CSV"],
        default="Return to main menu",
    ).ask()

    if next_action == "Output to CSV":
        export_json_to_csv(module)


def prepare_csv_rows(
    data: Dict[str, Any], stat_map: Optional[Dict[str, str]] = None
) -> List[List[str]]:
    rows = []
    if "weapon_id" in data:
        rows.append(["Weapon ID", data["weapon_id"]])
        rows.append(["Weapon Type", data["weapon_type"]])
        rows.append(["Weapon Tier", data["weapon_tier"]])
        rows.append(["Rounds Type", data["weapon_rounds_type"]])
        rows.append([])

        if stat_map:
            rows.append(["Base Stats"])
            for stat in data["base_stat"]:
                stat_name = stat_map.get(
                    stat["stat_id"], f"Unknown Stat ({stat['stat_id']})"
                )
                rows.append([stat_name, str(stat["stat_value"])])

            rows.append([])
            rows.append(["Firearm Attack (1-160)"])
            rows.append(["Level", "Type", "Value"])
            for level_info in data["firearm_atk"]:
                level = level_info["level"]
                for firearm in level_info["firearm"]:
                    stat_name = stat_map.get(
                        firearm["firearm_atk_type"],
                        f"Unknown Stat ({firearm['firearm_atk_type']})",
                    )
                    rows.append(
                        [str(level), stat_name, str(firearm["firearm_atk_value"])]
                    )
    else:
        rows.append(["Module Name", data["module_name"]])
        rows.append([])
        rows.append(["Level", "Capacity", "Value"])
        for stat in data["module_stat"]:
            rows.append(
                [str(stat["level"]), str(stat["module_capacity"]), stat["value"]]
            )

    return rows


def get_output_directory() -> Optional[str]:
    output_dir = questionary.path(
        "Select the output directory:",
        validate=lambda input: os.path.isdir(input)
        or f"The directory '{input}' is not valid.",
        only_directories=True,
    ).ask()

    if not output_dir:
        console.print("Invalid directory. Returning to main menu.")
        return None
    return output_dir


def get_csv_file_path(output_dir: str) -> Optional[str]:
    csv_file_name = questionary.text(
        "Enter the CSV file name (without extension):"
    ).ask()

    if not csv_file_name:
        console.print("Invalid file name. Returning to main menu.")
        return None

    return os.path.join(output_dir, f"{csv_file_name}.csv")


def export_json_to_csv(data: Dict[str, Any], stat_map: Dict[str, str] = None) -> None:
    output_dir = get_output_directory()
    if not output_dir:
        return

    csv_file_path = get_csv_file_path(output_dir)
    if not csv_file_path:
        return

    rows = prepare_csv_rows(data, stat_map)

    try:
        with open(csv_file_path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            for row in rows:
                csvwriter.writerow(row)
        console.print(f"Data successfully exported to {csv_file_path}.\n")
    except Exception as e:
        console.print(f"Failed to export data to CSV: {e}")

    questionary.text("Press enter to return to main menu").ask()


def load_data() -> Dict[str, Any]:
    print("Loading data...")
    weapons = load_weapon_data()
    stat_map = load_stat_data()
    modules = load_module_data()
    print(f"Loaded {len(weapons)} weapons and {len(modules)} modules.")
    return {
        "weapons": weapons,
        "stat_map": stat_map,
        "modules": modules,
        "weapon_names": [weapon["weapon_name"] for weapon in weapons],
        "module_names": [module["module_name"] for module in modules],
    }


def handle_refresh_cache() -> Dict[str, Any]:
    refresh_cache()
    return load_data()


def handle_search_weapons(
    weapons: List[Dict[str, Any]], stat_map: Dict[str, str], weapon_names: List[str]
) -> None:
    search_term = questionary.autocomplete(
        "Enter the weapon name to search for (or type 'exit' to quit):",
        choices=weapon_names,
    ).ask()

    if search_term is None or search_term.lower() == "exit":
        print("Exiting.")
        return
    if not search_term.strip():
        print("Search term cannot be empty. Please try again.")
        return

    results = search_items(weapons, search_term, "weapon_name")

    if not results:
        print(f"No weapons found matching '{search_term}'.")
    else:
        if len(results) > 1:
            selected_weapon = questionary.select(
                "Multiple weapons found. Please select one:",
                choices=[weapon["weapon_name"] for weapon in results],
            ).ask()
            weapon = next(
                weapon for weapon in results if weapon["weapon_name"] == selected_weapon
            )
        else:
            weapon = results[0]
        display_weapon_info(weapon, stat_map)


def handle_search_modules(
    modules: List[Dict[str, Any]], module_names: List[str]
) -> None:
    search_term = questionary.autocomplete(
        "Enter the module name to search for (or type 'exit' to quit):",
        choices=module_names,
    ).ask()

    if search_term is None or search_term.lower() == "exit":
        print("Exiting.")
        return
    if not search_term.strip():
        print("Search term cannot be empty. Please try again.")
        return

    results = search_items(modules, search_term, "module_name")

    if not results:
        print(f"No modules found matching '{search_term}'.")
    else:
        if len(results) > 1:
            selected_module = questionary.select(
                "Multiple modules found. Please select one:",
                choices=[module["module_name"] for module in results],
            ).ask()
            module = next(
                module for module in results if module["module_name"] == selected_module
            )
        else:
            module = results[0]
        display_module_info(module)


def main() -> None:
    data = load_data()

    try:
        while True:
            clear_screen()
            choice = questionary.select(
                "What would you like to do?",
                choices=["Search Weapons", "Search Modules", "Refresh Cache", "Exit"],
            ).ask()

            if choice is None or choice == "Exit":
                print("Exiting.")
                break

            if choice == "Refresh Cache":
                data = handle_refresh_cache()

            elif choice == "Search Weapons":
                handle_search_weapons(
                    data["weapons"], data["stat_map"], data["weapon_names"]
                )

            elif choice == "Search Modules":
                handle_search_modules(data["modules"], data["module_names"])

    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()

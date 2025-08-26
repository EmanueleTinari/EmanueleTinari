import subprocess
import json
from packaging.version import parse as parse_version

# Colori ANSI
RESET = "\033[0m"
WHITE = "\033[97m"
GREEN = "\033[92m"
RED = "\033[91m"

def colorize_version(version_inst, version_latest):
    v_inst = parse_version(version_inst)
    v_lat = parse_version(version_latest)
    version_colored = WHITE + version_inst + RESET
    if v_lat == v_inst:
        latest_colored = GREEN + version_latest + RESET
    elif v_lat > v_inst:
        latest_colored = RED + version_latest + RESET
    else:
        latest_colored = version_latest
    return version_colored, latest_colored

def main():
    result = subprocess.run(["pip", "list", "--outdated", "--format=json"], capture_output=True, text=True)
    packages = json.loads(result.stdout)

    print(f"{'Package':25} {'Version':10} {'Latest':10}")
    print("-"*50)
    for pkg in packages:
        ver_col, lat_col = colorize_version(pkg["version"], pkg["latest_version"])
        print(f"{pkg['name']:25} {ver_col:10} {lat_col:10}")

if __name__ == "__main__":
    main()

# %%
import site
import subprocess
import json
import shutil
import sys
import argparse
from pathlib import Path
from typing import List, Optional


# %%
def get_package_size(package_path: Path) -> float:
    """
    Get the size of a package (directory or file) in MB.


    Parameters:
    -----------
    package_path: Path, required
        Path to the package

    Returns:
    -----------
    total_size: float
        A float of package size in megabytes
    """

    if package_path.is_dir():
        # If it's a directory, sum the size of all files in the directory
        total_size = sum(
            f.stat().st_size for f in package_path.rglob("*") if f.is_file()
        )
    else:
        # If it's a single file (like a .dist-info), just get its size
        total_size = package_path.stat().st_size
    return total_size / (1024**2)  # Convert to MB

def parse_pyproject_dependencies(pyproject_path: Path) -> List[str]:
    """
    A method that naively reads a pyproject file in search of the dependencies string. It assumes the file is valid toml and a pyproject file.
    
    Args:
    ----
    pyproject_path: Path, required
        path to the pyproject file
    
    Returns:
    -------
    deps, List
        a python list of the dependencies
    """
    deps = []
    in_deps_block = False
    with pyproject_path.open("r") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("["):
                in_deps_block = False
            if stripped.startswith("dependencies = ["):
                in_deps_block = True
                continue
            if in_deps_block:
                if stripped.startswith("]"):
                    break
                dep = stripped.strip().strip(",").strip('"').strip("'")
                if dep:
                    name = dep.split(">=")[0].strip("==")[0].strip("<")[0].strip()
                    deps.append(name.lower())
    return deps

def parse_setup_cfg_dependencies(cfg_path: Path) -> List[str]:
    """
    A method that naively assumes a setup.cfg file contains your dependencies. It does not validate if the file is a setup.cfg file.

    Args:
    ----
    cfg_path: Path, required
        path to the setup.cfg file
    
    Returns:
    -------
    deps: List
        list of the dependencies
    """
    deps = []
    in_deps_block = False
    with cfg_path.open("r") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("["):
                in_deps_block = stripped.lower() == "[options]"
                continue
            if in_deps_block and stripped.lower().startswith("install_requires"):
                _, rest = stripped.split("=", 1)
                entries = rest.split("\n") + [next(f).strip() for _ in range(20)]
                for entry in entries:
                    entry = entry.strip().strip(",").strip('"').strip("'")
                    if not entry or entry.startswith("["):
                        break
                    name = entry.split(">=")[0].strip("==")[0].strip("<")[0].strip()
                    deps.append(name.lower())
                break
    return deps

def get_installed_packages(backend: str = "auto") -> List[dict]:
    """
    Returns a list of installed packages

    Automatically detects backend if not specified
    """
    if backend == "auto":
        backend = "uv" if shutil.which("uv") else "pip"
    
    if backend == "uv":
        cmd = ["uv", "pip", "list", "--format=json"]
    elif backend == "pip":
        cmd = [sys.executable, "-m", "pip", "list", "--format=json"]
    else:
        raise ValueError(f"Unknown backend: {backend}")
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to run: '{' '.join(cmd)}':\n{res.stderr}")

    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse output from '{' '.join(cmd)}'. Output:\n{res.stdout}")

def match_site_package(name: str, site_paths: List[Path]) -> Optional[Path]:
    """
    Tries to find the package based on its name and a list of paths
    """
    for site_path in site_paths:
        matches = list(site_path.glob(f"{name.replace('-','_')}*"))
        if matches:
            return matches[0]
    return None

def compute_package_sizes(package_names: List[str], site_paths: List[Path]) -> List[dict]:
    """
    Measures size of the packages

    Args:
    -----
    package_names: List[str], required
        list of packages names
    site_paths: List[Path], required
        list of package site paths

    Returns:
    --------
    results, dict
        a python dictionary containing packages and their size in Megabytes
    """
    results = []
    for name in package_names:
        path = match_site_package(name, site_paths)
        if not path:
            print(f"Warning: Could not find installed package for '{name}'")
            results.append({"name": name, "size_MB": None})
            continue
        try:
            size = get_package_size(path)
            results.append({"name": name, "size_MB": round(size, 2)})
        except Exception as e:
            print(f"Error measuring size of '{name}': {e}")
            results.append({"name": name, "size_MB": None})
    return results

def write_json(data: List[dict], file_path: Path) -> Path:
    """
    Write the results to a json file

    Args:
    -----
    data: List[dict], required
        the data we are writing to JSON
    file_path: Path, required
        path to the target JSON file
    
    Returns:
    --------
    file_path, Path
        the path to the JSON file that was written
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w") as f:
        json.dump(data, f, indent=2)
    return file_path

def list_total(package_sizes: List[dict]):
    """
    List the total size of packages in an app
    """
    large = [p for p in package_sizes if p["size_MB"] and p["size_MB"] >= 1]
    small = [p for p in package_sizes if p["size_MB"] and p["size_MB"] < 1]
    total = sum(p["size_MB"] for p in package_sizes if p["size_MB"] is not None)

    print(f"Total size of selected packages: {total:.2f} MB")
    print("=" * 50)
    print("Packages larger than 1 MB:")
    for p in sorted(large, key=lambda x: x["size_MB"], reverse=True):
        print(f"{p['name']}: {p['size_MB']} MB")
    print(f"\nPackages smaller than 1 MB: {len(small)} packages")
    print(f"Combined size of small packags: {sum(p['size_MB'] for p in small):.2f} MB")

#TODO: remove this?
def list_installed_packages_sizes():
    """
    List all installed packages in site-packages and their sizes.

    """
    site_packages_paths = (
        site.getsitepackages()
    )  # Get list of site-packages directories

    package_sizes = {}
    small_packages_count = 0
    small_packages_total_size = 0

    for site_package in site_packages_paths:
        site_package_path = Path(site_package)

        if site_package_path.exists():
            # Look for all subdirectories and files in the site-packages directory
            for package in site_package_path.iterdir():
                if package.is_dir() or package.suffix in {
                    ".py",
                    ".egg-info",
                    ".dist-info",
                }:
                    # Get the size of the package (dir or single file like .egg-info)
                    size = get_package_size(package)
                    package_sizes[package.name] = size

    # Split packages into two groups: larger than 1MB and smaller than 1MB
    large_packages = {}
    small_packages_total_size = 0
    small_packages_count = 0
    total_size = 0

    for package_name, size in package_sizes.items():
        total_size += size
        if size >= 1:
            large_packages[package_name] = size
        else:
            small_packages_count += 1
            small_packages_total_size += size

    # Sort the large packages by size
    sorted_large_packages = sorted(
        large_packages.items(), key=lambda x: x[1], reverse=True
    )

    # Print total size of all packages
    print(f"Total size of all packages: {total_size:.2f} MB")

    # Print a separator
    print("=" * 50)

    # Print the large packages
    print("Packages larger than 1 MB:")
    for package_name, size in sorted_large_packages:
        print(f"{package_name}: {size:.2f} MB")

    # Print summary of small packages
    print(f"\nPackages smaller than 1 MB: {small_packages_count} packages")
    print(
        f"Combined size of packages smaller than 1 MB: {small_packages_total_size:.2f} MB"
    )

# TODO: remove this?
def get_pip_packages(
    main_only=False, main_req_file: Path = Path("requirements/main.txt")
):
    """
    Gets a list of packages in json using "pip list --format=json"

    If main_only is True, limits to the main group (excluding dev).
    """
    res = subprocess.run(
        ["uv", "pip", "list", "--format=json"], capture_output=True, text=True
    )

    try:
        packages = json.loads(res.stdout)
    except json.JSONDecodeError:
        print("Error: Failed to parse uv pip list output")
        return []

    if main_only and main_req_file.exists():
        main_deps = read_requirements_file(main_req_file)
        packages = [pkg for pkg in packages if pkg["name"].lower() in main_deps]

    return packages

# TODO: remove?
def write_deps_json(data: dict, file_path: Path):
    """
    Get list of packages, check each package size, and append to the dict before writing to json

    Parameters:
    -----------
    data: dict, Required
        the dictionary of packages from the get_pip_packages method
    file_path: Path, Required
        the posix path to write the JSON file to

    Returns:
    --------
    f, the JSON file including the path it is stored on.
    """
    site_packages_paths = site.getsitepackages()
    enriched_data = []

    for package in data:
        package_name = package["name"]
        package_version = package["version"]
        package_size = None

        # Attempt to find the package in site-packages
        for site_package in site_packages_paths:
            site_package_path = Path(site_package)

            # Look for folders or files that match the package name
            potential_matches = list(site_package_path.glob(f"{package_name}*"))

            if potential_matches:
                # Use the first match found
                package_path = potential_matches[0]
                package_size = get_package_size(package_path)
                break

        # Append to enriched data
        enriched_data.append(
            {
                "name": package_name,
                "version": package_version,
                "size_MB": round(package_size, 2) if package_size is not None else None,
            }
        )

    # Write to JSON
    file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with open(file_path, "w") as f:
        json.dump(enriched_data, f, indent=2)

    return file_path

# TODO: remove this?
def read_requirements_file(path: Path) -> List[str]:
    """
    Read a pip-compile style requirements file and return package names only.
    """
    package_names = []

    with path.open("r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or line.startswith("-r"):
                continue

            # Remove extras, version pins, hashes, etc.
            name = line.split("[")[0].split("==")[0].split(">")[0].split("<")[0]
            package_names.append(name.lower())

    return package_names



# %%
def main():
    description = "depsize: Get the total size of installed python dependencies in MB. \n Run 'depsize total' to get a summary including total size and the largest packages. \n Run 'depsize --o FILE' to export as JSON, f.ex 'depsize --o data/packages.json'"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "command",
        nargs="?",
        choices=["total"],
        help="Subcommand to run. Use 'total' to get size summary.",
    )
    parser.add_argument(
        "--o",
        "--output",
        dest="output_path",
        type=Path,
        help="Path to output JSON file, f.ex data/packages.json",
    )
    parser.add_argument(
        "--main", action="store_true", help="Only include main dependencies"
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=Path("requirements/main.txt"),
        help="Path to the requirements txt file --main mode ",
    )

    args = parser.parse_args()

    if args.command == "total":
        list_installed_packages_sizes()
    elif args.output_path:
        data = get_pip_packages(main_only=args.main, main_req_file=args.requirements)
        output_path = write_deps_json(data, args.output_path)
        print(f"Dependencies written to {output_path}")
    else:
        print(description)


if __name__ == "__main__":
    main()
# %%

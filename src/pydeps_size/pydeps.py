# %%
import site
from pathlib import Path
import subprocess
import json
import argparse


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


def get_pip_packages():
    """
    Gets a list of packages in json using "pip list --format=json"
    """
    res = subprocess.run(
        ["uv", "pip", "list", "--format=json"], capture_output=True, text=True
    )
    return json.loads(res.stdout)


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


# %%
def main():
    description = "pydeps: Get the total size of installed python dependencies in MB. \n Use 'pydeps total' to get a summary including total size and the largest packages. \n Use 'pydeps --o FILE' to export as JSON, f.ex 'pydeps --o data/packages.json'"
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

    args = parser.parse_args()

    if args.command == "total":
        list_installed_packages_sizes()
    elif args.output_path:
        data = get_pip_packages()
        output_path = write_deps_json(data, args.output_path)
        print(f"Dependencies written to {output_path}")
    else:
        print(description)


if __name__ == "__main__":
    main()
# %%

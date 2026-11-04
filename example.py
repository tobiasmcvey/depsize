# %%
from pathlib import Path

from src.depsize.depsize import (
    get_package_size,
    get_pip_packages,
    list_installed_packages_sizes,
    write_deps_json,
)

# %%
# get size of a directory
get_package_size(package_path=Path(".venv"))
# %%
# get size of a specific package
package = "IPython"
py_version = 3.11
get_package_size(
    package_path=Path(f".venv/lib/python{py_version}/site-packages/{package}")
)
# %%
list_installed_packages_sizes()  # regular program
# %%
# write a json file with each dependency, version number and size in MB
write_deps_json(data=get_pip_packages(), file_path=Path("../../data/deps.json"))

# %%

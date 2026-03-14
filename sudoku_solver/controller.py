from collections.abc import Iterable
import os
from pathlib import Path
import subprocess


__all__ = ["create_ps_script", "run_ps_script"]


def create_ps_script(inputs: Iterable) -> str:
    script_index = 0
    while Path(f"script_{script_index}.ps1").exists():
        script_index += 1
    script_name = f"script_{script_index}.ps1"

    with open(script_name, "w+") as fp:
        fp.write("$wshell = New-Object -ComObject wscript.shell;\n")
        fp.write("Start-Sleep -Milliseconds 3000;\n")
        fp.writelines(f"$wshell.SendKeys('{key}');" for key in inputs)

    return script_name


def run_ps_script(path: str) -> None:
    print(
        "\n\033[32menter 'r' key to trigger the script and switch to the sudoku game window\033[0m"
    )
    subprocess.run(
        ["powershell.exe", "-ExecutionPolicy", "Unrestricted", "-File", path]
    )
    os.remove(path)

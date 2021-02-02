#!/usr/bin/env python3

# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

import argparse
import datetime
import os
import platform
import pwd
import subprocess
import textwrap


def username():
    return pwd.getpwuid(os.getuid())[0]


def generate_build_info_c(configuration):
    gcc_version = subprocess.run(
        ["arm-none-eabi-gcc", "-dumpversion"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    release = subprocess.run(
        ["git", "describe", "--always", "--tags", "--abbrev=0"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    year, month, day = release.split(".", 3)

    revision = subprocess.run(
        ["git", "describe", "--always", "--tags", "--dirty"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    compiler = f"gcc {gcc_version}"

    date = datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M UTC")

    machine = f"{username()}@{platform.node()}"

    build_info_string = (
        f"{revision} ({configuration}) on {date} with {compiler} by {machine}"
    )

    return build_info_string, textwrap.dedent(
        f"""
    /* This file is generated by generate_build_info.py - don't edit it directly!! */

    #include "wntr_build_info.h"

    static const char compiler[] = "{compiler}";
    static const char revision[] = "{revision}";
    static const char date[] = "{date}";
    static const char machine[] = "{machine}";
    static const char release[] = "{release}";
    static const char build_info[] = "{build_info_string}";

    struct WntrBuildInfo wntr_build_info() {{
        return (struct WntrBuildInfo){{
            .revision = revision,
            .date = date,
            .compiler = compiler,
            .machine = machine,
            .release = release,
            .release_year = {year},
            .release_month = {month},
            .release_day = {day},
        }};
    }}

    const char* wntr_build_info_string() {{ return build_info; }}
    """
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "--configuration", default="Unknown")
    parser.add_argument("output", type=argparse.FileType("w", encoding="utf-8"))

    args = parser.parse_args()

    info, output = generate_build_info_c(args.config)

    args.output.write(output)

    print(f"Build ID: {info}")


if __name__ == "__main__":
    main()
from __future__ import annotations

import os
import os.path
import random
import string
from glob import glob

import bcrypt
import click
import pkg_resources
from tutor import hooks

from .__about__ import __version__

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'RALPH_'.
        ("RALPH_VERSION", __version__),
        ("DOCKER_IMAGE_RALPH", "docker.io/fundocker/ralph:3.6.0"),
        # Change to https:// if the public interface to it is secure
        ("RALPH_RUN_HTTPS", False),
        ("RALPH_HOST", "ralph"),
        ("RALPH_PORT", "8100"),
        ("RALPH_ENABLE_PUBLIC_URL", False),
        ("RALPH_SENTRY_DSN", ""),
        ("RALPH_EXECUTION_ENVIRONMENT", "development"),
        ("RALPH_SENTRY_CLI_TRACES_SAMPLE_RATE", 1.0),
        ("RALPH_SENTRY_LRS_TRACES_SAMPLE_RATE", 0.1),
        ("RALPH_SENTRY_IGNORE_HEALTH_CHECKS", True),
    ]
)

# Ralph requires us to write out a file with pre-encrypted values, so we encrypt
# them here per: https://openfun.github.io/ralph/api/#creating_a_credentials_file
#
# They will remain unchanged between config saves as usual and the unencryted
# passwords will still be able to be printed.
RALPH_ADMIN_PASSWORD = "".join(random.choice(string.ascii_lowercase) for i in range(36))
RALPH_LMS_PASSWORD = "".join(random.choice(string.ascii_lowercase) for i in range(36))
RALPH_ADMIN_HASHED_PASSWORD = bcrypt.hashpw(
    RALPH_ADMIN_PASSWORD.encode(), bcrypt.gensalt()
).decode("ascii")
RALPH_LMS_HASHED_PASSWORD = bcrypt.hashpw(
    RALPH_LMS_PASSWORD.encode(), bcrypt.gensalt()
).decode("ascii")

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'RALPH_'.
        # For example:
        ### ("RALPH_SECRET_KEY", "{{ 24|random_string }}"),
        ("RALPH_ADMIN_USERNAME", "ralph"),
        ("RALPH_ADMIN_PASSWORD", RALPH_ADMIN_PASSWORD),
        ("RALPH_ADMIN_HASHED_PASSWORD", RALPH_ADMIN_HASHED_PASSWORD),
        ("RALPH_LMS_USERNAME", "lms"),
        ("RALPH_LMS_PASSWORD", RALPH_LMS_PASSWORD),
        ("RALPH_LMS_HASHED_PASSWORD", RALPH_LMS_HASHED_PASSWORD),
        ("RUN_RALPH", True),
    ]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        ### ("PLATFORM_NAME", "My platform"),
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutorralph/templates/ralph/jobs/init/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutorralph/templates/ralph/jobs/init/lms.sh
    # And then add the line:
    ### ("lms", ("ralph", "jobs", "init", "lms.sh")),
]


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = pkg_resources.resource_filename(
        "tutorralph", os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


########################################
# DOCKER IMAGE MANAGEMENT
########################################


# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/ralph/build/myimage,
        # and then write:
        (
            "ralph",
            ("plugins", "ralph", "build"),
            "development",  # "docker.io/ralph:{{ RALPH_VERSION }}",
            ("--target=development",),
        ),
    ]
)


# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ RALPH_VERSION }}",
        ### ),
    ]
)


# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ RALPH_VERSION }}",
        ### ),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        pkg_resources.resource_filename("tutorralph", "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutorralph/templates/ralph/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/ralph/build``.
    [
        ("ralph/build", "plugins"),
        ("ralph/apps", "plugins"),
    ],
)

########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutorralph/patches,
# apply a patch based on the file's name and contents.
for path in glob(
    os.path.join(
        pkg_resources.resource_filename("tutorralph", "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################

# A job is a set of tasks, each of which run inside a certain container.
# Jobs are invoked using the `do` command, for example: `tutor local do importdemocourse`.
# A few jobs are built in to Tutor, such as `init` and `createuser`.
# You can also add your own custom jobs:

# To add a custom job, define a Click command that returns a list of tasks,
# where each task is a pair in the form ("<service>", "<shell_command>").
# For example:
### @click.command()
### @click.option("-n", "--name", default="plugin developer")
### def say_hi(name: str) -> list[tuple[str, str]]:
###     """
###     An example job that just prints 'hello' from within both LMS and CMS.
###     """
###     return [
###         ("lms", f"echo 'Hello from LMS, {name}!'"),
###         ("cms", f"echo 'Hello from CMS, {name}!'"),
###     ]


# Then, add the command function to CLI_DO_COMMANDS:
## hooks.Filters.CLI_DO_COMMANDS.add_item(say_hi)

# Now, you can run your job like this:
#   $ tutor local do say-hi --name="Open edX"


#######################################
# CUSTOM CLI COMMANDS
#######################################

# Your plugin can also add custom commands directly to the Tutor CLI.
# These commands are run directly on the user's host computer
# (unlike jobs, which are run in containers).

# To define a command group for your plugin, you would define a Click
# group and then add it to CLI_COMMANDS:


### @click.group()
### def ralph() -> None:
###     pass


### hooks.Filters.CLI_COMMANDS.add_item(ralph)


# Then, you would add subcommands directly to the Click group, for example:


### @ralph.command()
### def example_command() -> None:
###     """
###     This is helptext for an example command.
###     """
###     print("You've run an example command.")


# This would allow you to run:
#   $ tutor ralph example-command

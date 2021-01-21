#!/usr/bin/env python3

from sparrow_cli._hacks import load_envbash_init_hack

load_envbash_init_hack()

# Proceed with normal CLI initialization in all other cases

from sparrow_cli import cli

cli()

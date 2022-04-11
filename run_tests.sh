#!/bin/bash
set -e

pytest --disable-warnings
pylint treasure_island

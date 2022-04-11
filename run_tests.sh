#!/bin/bash
set -e

pylint treasure_island
pytest --disable-warnings

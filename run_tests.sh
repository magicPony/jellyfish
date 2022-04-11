#!/bin/bash
pytest --disable-warnings
pylint treasure_island --ignore-paths=^treasure_island/testing/.*$

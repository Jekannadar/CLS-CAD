#!/bin/bash
poetry run nuitka --standalone --onefile --include-module=cls_cps.server --include-module=montydb.storage.flatfile --include-package=dns --assume-yes-for-downloads --output-dir=build --enable-plugin=tk-inter --include-data-dir=cls_cps/static=cls_cps/static -o clscps.bin main.py

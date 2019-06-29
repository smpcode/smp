#!/usr/bin/env bash

# auto_generate_model
# ~~~~~~~~~~~~

# :authors: smpcode
# :version: 1.0 of 2018-06-07
# :copyright: (c) 2018 smpcode

table_name=$1

python -m pwiz --host=127.0.0.1 --port=4316 -P smp@bj1301 -e mysql --user=smp -t $table_name smp

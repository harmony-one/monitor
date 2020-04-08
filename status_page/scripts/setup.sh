#!/usr/bin/env bash

root=`git rev-parse --show-toplevel`
auth_file=${root}"/status_page/watchdog_authentication.txt"

if [[ ! -f "$auth_file" ]]; then
  echo 'username
password' > $auth_file
fi

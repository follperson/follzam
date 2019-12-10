#!/usr/bin/env bash
# https://www.cyberciti.biz/tips/linux-unix-pause-command.html
# https://stackoverflow.com/questions/3349105/how-to-set-current-working-directory-to-the-directory-of-the-script
function pause(){
    read -p "$*"
}

cd "$(dirname "$0")"
pytest -v follzam/tests/*.py
pause 'Press [Enter] key to continue'
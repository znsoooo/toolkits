@echo off

set host=127.0.0.1
set url=http://%host%:8000/simple/

pip config set global.no-index true
pip config set global.find-links %url%
pip config set global.trusted-host %host%

pause

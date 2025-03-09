@echo off

call:create "Alarms"
call:create "Android"
call:create "Audiobooks"
call:create "DCIM"
call:create "Documents"
call:create "Download"
call:create "LOST.DIR"
call:create "Movies"
call:create "Music"
call:create "Notifications"
call:create "Pictures"
call:create "Podcasts"
call:create "Recordings"
call:create "Ringtones"
call:create "System Volume Information"
pause

:create
echo. > %1
attrib +h +s %1
goto :eof

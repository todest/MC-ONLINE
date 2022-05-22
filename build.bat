@echo off
pyinstaller -w -F main.pyw -p ui -p utils --clean -i icon.ico -y -n mc-online

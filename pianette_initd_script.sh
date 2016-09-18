#!/bin/sh
### BEGIN INIT INFO
# Provides:          pianette
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: pianette
# Description:       pianette firmware
### END INIT INFO

case "$1" in
    start)
        sudo -i PYTHONIOENCODING="utf-8" /home/pi/pianette/main.py --enable-source gpio --enable-source api --select-game 'street-fighter-alpha-3' --select-player 1
    ;;

    stop)
        sudo killall python3
    ;;

    *)
        echo 'Usage: /etc/init.d/pianette {start|stop}'
        exit 1
    ;;
esac

exit 0
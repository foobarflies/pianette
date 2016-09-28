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

is_running(){
    running_processes=`ps axf | grep "python3 /home/pi/pianette/main.py" | wc -l`

    if [ "$running_processes" -ge 2 ]; then
        echo 1
    else
        echo 0
    fi
}

ok(){
    printf "\033[s\033[0A\033[1C\033[1;32mok\033[u\033[0m"
}

case "$1" in
    start)
        sudo -i PYTHONIOENCODING="utf-8" /home/pi/pianette/main.py --enable-source gpio --enable-source api --select-game 'street-fighter-alpha-3' --select-player 1
    ;;

    stop)
        if [ "$(is_running)" -eq "1" ]; then
            printf "[..] Stopping Pianette ...\n"
            sudo killall python3
            ok
         else
            printf "Pianette is \033[31mstopped\033[0m\n"
        fi
    ;;

    force-stop)
        
        printf "[..] Force-stopping Pianette ...\n"
        sudo killall python3 > /dev/null 2>&1
        ok
    ;;

    status)
        if [ "$(is_running)" -eq "1" ]; then
            printf "Pianette is \033[32mrunning\033[0m\n"
        else
            printf "Pianette is \033[31mstopped\033[0m\n"
        fi
    ;;

    restart)
        $0 stop
        if [ "$(is_running)" -eq "1" ]; then
            printf "Unable to stop, will not attempt to start\n"
            exit 1
        fi
        $0 start
    ;;

    *)
        printf '\033[1mControls the pianette instance.\033[0m\n'
        printf 'Usage: sudo service pianette {start|stop|force-stop|restart|status}\n'
        exit 1
    ;;
esac

exit 0
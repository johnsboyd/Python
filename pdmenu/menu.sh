#!/bin/bash
# see this page for emulating keyboard with gpio buttons
# https://github.com/PiSupply/PaPiRus/issues/167
# https://forum.emteria.com/discussion/752/raspberry-gpio-buttons-as-input-keys
# example:  dtoverlay=gpio-key,gpio=13,gpio_pull=up,label=GPIO_Enter,keycode=28

# puredata -nogui -midiindev  1,2 -midioutdev 1,2 -open countup.pd

function setup(){
    PID=""
    lastpre=""
    MIDIINDEV=""
    MIDIOUTDEV=""
    rm -f /dev/midi1 /dev/midi2
    mn=1
    for mp in `ls -1 /dev/snd/midiC*`
    do
        ln -s $mp /dev/midi${mn}
        let "mn+=1"
    done
    if [ "$mn" -gt "2" ];then
        MIDIINDEV="-midiindev 1,2"
        MIDIOUTDEV="-midioutdev 1,2"
    else
        MIDIINDEV="-midiindev 1"
        MIDIOUTDEV="-midioutdev 1"
    fi
}

function main_menu(){
    selection=$(dialog --nook --no-cancel --stdout --no-shadow --menu "select function:" 12 24 4 0 Load 1 Info 2 Halt 3 Exit)
    case $selection in
    0) loadprog
       ;;
    1) showinfo
       ;;
    2) turnoff
       ;;
    3) exitout
       ;;
    esac
}

function showinfo(){
    hostname -I | awk '{print "IP:",$1}' > info.txt
    uptime | awk '{print "Load:", $9,$10,$11}' | tr -d ',' >> info.txt
    free -m | grep Mem: | awk '{printf "Mem: %s/%s MB\n",$3,$2}' >> info.txt
    df -h | grep /dev/root | awk '{printf "Disk: %s/%s\n",$3,$2}' >> info.txt
    dialog --title " Info" --exit-label "ok" --no-shadow --textbox info.txt 12 24
    rm -f info.txt
    main_menu
}

function loadprog(){
    ls -1 *.pd | awk '{printf " %x %s\n", NR-1, $0}' > plist
    tot=$(wc -l plist | awk '{print $1}')
    out=$(dialog --nook --cancel-label "esc" --stdout --no-shadow --menu "select program:" 12 24 ${tot} --file plist)
    if [ -z "$out" ];then
        rm -f plist
        main_menu
    else
        preset=$(grep "^ ${out} " plist | awk '{print $2}')
        rm -f plist
        if [ "$preset" != "$lastpre"  ];then
            if [ -n "$PID" ];then
                kill $PID
            fi
            puredata -nogui $MIDIINDEV $MIDIOUTDEV -open $preset 2>&1 | sed -n 's/print: symbol //;s/print: list //;w pdout.log' &
            PID=$!
            let "PID-=1"
        fi
        lastpre=$preset
        dialog --title ${preset} --exit-label "ok" --no-shadow --tailbox pdout.log 12 24
        main_menu
    fi
}

function turnoff(){
    dialog --title 'Shutdown' --ok-label yes --help-button --help-label esc --no-shadow --msgbox "Are you sure?" 12 24 
    if [ "$?" -eq "0" ];then
        exitout
        dialog --title "Message" --no-shadow --infobox "Unplug the pi after the green LED goes out" 0 0
        sleep 3
        halt
    else
        main_menu
    fi
}

function exitout(){
    if [ -n "$PID" ];then
        kill $PID
    fi
    rm -f pdout.log
    rm -f plist
}

function main(){
    setup
    main_menu
}

main

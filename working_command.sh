#!/bin/sh
# st -f 'SauceCodePro Nerd Font Mono:size=10' -e sh -c '{ ./track_hand.py | 2>/dev/null ffmpeg -y -f rawvideo -s 640x480 -pix_fmt bgr24 -i - -map 0:V:0 -filter:v "format=gray,hflip" -c:v libx265 -preset ultrafast -tune zerolatency -crf 30 -f nut - | TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv --really-quiet --no-cache --no-config --vo=caca --untimed --profile=low-latency - || { echo Error 1>&2; read X; }; } | ./game.py'
# st -f 'SauceCodePro Nerd Font Mono:size=10' -e sh -c '{ ./track_hand.py | 2>/dev/null ffmpeg -y -f rawvideo -s 640x480 -pix_fmt bgr24 -i - -map 0:V:0 -filter:v "format=gray,hflip" -c:v libx265 -preset ultrafast -tune zerolatency -crf 30 -f nut - | TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv --really-quiet --no-cache --no-config --vo=caca --untimed --profile=low-latency - || { echo Error 1>&2; read X; }; }'
# st -f 'SauceCodePro Nerd Font Mono:size=10' -e sh -c '{ ./track_hand.py | 2>/dev/null ffmpeg -y -f rawvideo -s 640x480 -pix_fmt bgr24 -i - -map 0:V:0 -filter:v "format=gray,hflip" -c:v libx264 -preset ultrafast -tune zerolatency -crf 30 -f nut - | TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv --really-quiet --no-cache --no-config --vo=tct --untimed --profile=low-latency - || { echo Error 1>&2; read X; }; }'

xterm \
	-bg black \
	-fg white \
	-s -fullscreen \
	-fa 'SauceCodePro Nerd Font Mono' \
	-fs 8 \
	-e '{
		./track_hand.py |
		2>/dev/null ffmpeg -y \
			-f rawvideo \
			-s 640x480 \
			-pix_fmt bgr24 \
			-i - \
			-map 0:V:0 \
			-filter:v "format=gray,hflip" \
			-c:v libx265 \
			-preset ultrafast \
			-tune zerolatency \
			-crf 30 \
			-f nut \
			- |
		TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv \
			--really-quiet \
			--no-cache \
			--no-config \
			--vo=caca \
			--untimed \
			--profile=low-latency \
			- \
		|| { echo Error 1>&2; read X; };
	}'

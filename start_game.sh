#!/bin/sh
# st -f 'SauceCodePro Nerd Font Mono:size=10' -e sh -c '{ ./game.py | 2>/dev/null ffmpeg -y -f rawvideo -s 640x480 -pix_fmt bgr24 -i - -map 0:V:0 -filter:v "format=gray,hflip" -c:v libx265 -preset ultrafast -tune zerolatency -crf 30 -f nut - | TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv --really-quiet --no-cache --no-config --vo=caca --untimed --profile=low-latency - || { echo Error 1>&2; read X; }; } | ./game.py'
# st -f 'SauceCodePro Nerd Font Mono:size=10' -e sh -c '{ ./game.py | 2>/dev/null ffmpeg -y -f rawvideo -s 640x480 -pix_fmt bgr24 -i - -map 0:V:0 -filter:v "format=gray,hflip" -c:v libx265 -preset ultrafast -tune zerolatency -crf 30 -f nut - | TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv --really-quiet --no-cache --no-config --vo=caca --untimed --profile=low-latency - || { echo Error 1>&2; read X; }; }'
# st -f 'SauceCodePro Nerd Font Mono:size=10' -e sh -c '{ ./game.py | 2>/dev/null ffmpeg -y -f rawvideo -s 640x480 -pix_fmt bgr24 -i - -map 0:V:0 -filter:v "format=gray,hflip" -c:v libx264 -preset ultrafast -tune zerolatency -crf 30 -f nut - | TERM=xterm-mono CACA_DRIVER=ncurses DISPLAY= mpv --really-quiet --no-cache --no-config --vo=tct --untimed --profile=low-latency - || { echo Error 1>&2; read X; }; }'

export TERM_FONT='SauceCodePro Nerd Font Mono'
export TERM_FONT_SIZE='10'
export OUT_TERM='xterm-mono'
xterm \
	-bg black \
	-fg white \
	-s -fullscreen \
	-fa "${TERM_FONT}" \
	-fs "${TERM_FONT_SIZE}" \
	-e '{
		./game.py |
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
		TERM='"'${OUT_TERM}'"' CACA_DRIVER=ncurses DISPLAY= mpv \
			--really-quiet \
			--no-cache \
			--no-config \
			--vo=caca \
			--untimed \
			--profile=low-latency \
			- \
		|| { echo "There was an error" 1>&2; read X; };
	}'

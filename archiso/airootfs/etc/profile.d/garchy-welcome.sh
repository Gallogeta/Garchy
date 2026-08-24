#!/bin/sh
if [ -t 0 ] && [ "$TERM" != "dumb" ]; then
    echo "\033[96m\033[1m"
    cat << "BANNER"
   ██████╗  █████╗ ██████╗  ██████╗██╗  ██╗██╗   ██╗
  ██╔════╝ ██╔══██╗██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝
  ██║  ███╗███████║██████╔╝██║     ███████║ ╚████╔╝ 
  ██║   ██║██╔══██║██╔══██╗██║     ██╔══██║  ╚██╔╝  
  ╚██████╔╝██║  ██║██║  ██║╚██████╗██║  ██║   ██║   
   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   
BANNER
    echo "       \033[94mMinimal • Gaming & Dev Ready • Built-in AI\033[0m\n"
    echo "  🚀 To install Garchy OS, run: \033[92m\033[1mgarchy-installer\033[0m"
    echo "  🤖 To test Garchy AI, run:      \033[93m\033[1mai status\033[0m\n"
fi

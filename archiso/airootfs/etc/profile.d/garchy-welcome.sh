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
    echo "       \033[94mMinimalist • 144Hz Gaming & Dev Stack • Cephalon AI\033[0m\n"
    echo "  🚀 Graphical Installer:  \033[92m\033[1mgarchy-gui-installer\033[0m"
    echo "  ⌨️  Terminal Installer:   \033[93m\033[1mgarchy-installer\033[0m\n"
fi

#!/bin/bash

if [ -z "$DISPLAY" ]; then
  echo "Nenhum DISPLAY detectado. Iniciando Xvfb e Servidor VNC..."
  Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
  sleep 2
  export DISPLAY=:99
  
  # Inicia o servidor VNC na tela virtual :99
  # -nopw: sem senha (cuidado, use apenas para debug)
  # -forever: não fecha quando você desconecta
  x11vnc -display :99 -nopw -forever -shared -bg -quiet
  echo "Servidor VNC iniciado na porta 5900"
else
  echo "DISPLAY detectado ($DISPLAY). Usando a tela do seu computador..."
fi

echo "Iniciando script Python..."
python -u main.py

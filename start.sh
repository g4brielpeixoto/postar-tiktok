#!/bin/bash

if [ -z "$DISPLAY" ]; then
  echo "Nenhum DISPLAY detectado. Iniciando Xvfb para tela virtual..."
  Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
  sleep 2
  export DISPLAY=:99
  
  if [ "$ENABLE_VNC" = "true" ]; then
    echo "Iniciando Servidor VNC na porta 5900..."
    # -nopw: sem senha (cuidado, use apenas para debug)
    # -forever: não fecha quando você desconecta
    x11vnc -display :99 -nopw -forever -shared -bg -quiet
    echo "VNC acessível na porta 5900"
  else
    echo "VNC desabilitado (ENABLE_VNC != true)"
  fi
else
  echo "DISPLAY detectado ($DISPLAY). Usando a tela do seu computador..."
fi

echo "Iniciando script Python..."
python -u main.py

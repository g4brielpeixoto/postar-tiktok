#!/bin/bash

if [ -z "$DISPLAY" ]; then
  echo "Nenhum DISPLAY detectado. Iniciando Xvfb para tela virtual..."
  Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
  sleep 2
  export DISPLAY=:99
else
  echo "DISPLAY detectado ($DISPLAY). Usando a tela do seu computador..."
fi

echo "Iniciando script Python..."
python -u main.py

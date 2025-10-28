#!/bin/sh
# El script debe insertarse en el crontab de root y debe
# copiarse en el directorio /root/bin, cree la entrada    
# escribiendo "crontab -e" e inserte:
# --------------------------------------------------
# 0-59/1 * * * *         /root/bin/diskmax.sh >/dev/null 2>&1
# ---------------------------------------------------
MAX=85

PART=sda1
USE=`df -ih |grep $PART | awk '{ print $5 }' | cut -d'%' -f1 | uniq -c | awk '{ print $2 }'`
echo "¿ $USE > $MAX ?"
if [ $USE -gt $MAX ]; then
  #  echo "Percent used: $USE" 
  #  echo "Superado: $MAX"
  /root/bin/optimiza.sh ; /root/bin/reiniciaservicios.sh
fi
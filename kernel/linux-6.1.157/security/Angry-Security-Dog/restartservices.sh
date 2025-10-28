#Este script, debes incluirlo en tu crond, puedes incluirlo en /etc/cron.d/ creando un fichero llamado "cargatrabajo.cron" e incluir:
#
#   0-59/1 * * * * root /root/bin/cargatrabajo.sh 
#
#O si lo ingresas en crontab con "crontab -e" haz la entrada que tenga:
#
#    0-59/1 * * * * /root/bin/cargatrabajo.sh */
      
load_conf()
{
        CONF="/root/bin/reiniciaservicios.conf"
        if [ -f "$CONF" ] && [ ! "$CONF" ==  "" ]; then
                source $CONF
        else
                head
                echo "\$CONF not found."
                exit 1
        fi
}

load_conf

# Comprobar que el campo "uptime" a leer, es el correcto
A=`uptime | awk '{print $10}' | cut -d, -f1`
if [ `expr $A : '[0-9].[0-9]*'` -eq ${#A} ] ; then
   echo " "
else 
    A=`uptime | awk '{print $11}' | cut -d, -f1`
fi

PARAR=1         # Bandera del bucle
UNAVEZ=1        # Bandera del buble


while [[ $( echo "$A > $B" | bc ) -eq 1 ]]; do

  if [ $PARAR -eq 1 ] ; then
     
     if [ $UNAVEZ -eq 1 ] ; then
        /sbin/service httpd stop        >> $REGISTROSLOGS
        printf "\n"                     >> $REGISTROSLOGS
        /sbin/service mysqld stop       >> $REGISTROSLOGS
        printf "\n"                     >> $REGISTROSLOGS
        sleep 3
     fi
     UNAVEZ=0   # Ya no leera "if" durante el bucle
  fi
  PARAR=0       # Ya no leera "if" durante el bucle

 A=`uptime | awk '{print $10}' | cut -d, -f1`

 if [ `expr $A : '[0-9].[0-9]*'` -eq ${#A} ] ; then
   source $CONF
 else
    A=`uptime | awk '{print $11}' | cut -d, -f1`
 fi
 sleep 2

done


if [ $PARAR -eq 0 ] ; then
    sleep 3
    /sbin/service mysqld start  >> $REGISTROSLOGS
    printf "\n"                 >> $REGISTROSLOGS
    /sbin/service httpd start   >> $REGISTROSLOGS
    printf "\n"                 >> $REGISTROSLOGS   
fi
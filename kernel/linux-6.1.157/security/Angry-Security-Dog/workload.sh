#!/bin/sh
# El script debe insertarse en el crontab de root y debe
# copiarse en el directorio /root/bin, cree la entrada
# escribiendo "crontab -e" e inserte:
# --------------------------------------------------
# 
# 0-59/1 * * * *         /root/bin/cargatrabajo.sh >/dev/null 2>&1
# ---------------------------------------------------

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

TMP_PREFIX='/tmp/cargatrabaj'
TMP_FILE="mktemp $TMP_PREFIX.XXXXXXXX"

FINMSG=0
A=`uptime | awk '{print $10}' | cut -d, -f1`
if [ `expr $A : '[0-9].[0-9]*'` -eq ${#A} ] ; then
  source $CONF
else 
  A=`uptime | awk '{print $11}' | cut -d, -f1`
fi


echo "¿ $A > $B ?"
if [ $( echo "$A > $B" | bc ) -eq 1 ]; then
        FINMSG=1
        echo "=============================="                   >> $REGISTROSLOGS
        echo "START: $A > $B - `date` - `uptime` - `hostname`"  >> $REGISTROSLOGS
        echo "`/root/bin/conexiones.sh`"                        >> $REGISTROSLOGS
        echo "=============================="                   >> $REGISTROSLOGS
        /root/bin/reiniciaservicios.sh ; sleep 3
        /root/bin/cargatrabajo.sh
fi

if [ $FINMSG -eq 1 ] ; then
        printf "\n"                                             >> $REGISTROSLOGS
        echo "END: $A > $B - `date` - `uptime` - `hostname`"    >> $REGISTROSLOGS
        FINMSG=0
fi


rm -fv $TMP_PREFIX.*
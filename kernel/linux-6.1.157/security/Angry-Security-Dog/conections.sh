#el script liveconections esta basado en este es importante

netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n | tail 
NumConex=`netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | sort -nr | uniq -c | awk '{sum+=$1} END {print sum}'`

A=`uptime | awk '{print $10}' | cut -d, -f1`
if [ `expr $A : '[0-9].[0-9]*'` -eq ${#A} ] ; then
  echo "Number";
else
    A=`uptime | awk '{print $11}' | cut -d, -f1`
fi
    
echo "$NumConex conexiones, -> carga trabajo: $A"

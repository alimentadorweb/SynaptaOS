#script para vigilar conexiones

for i in {1..20}; do 
        clear; conexiones.sh ; date; diskmax.sh; sleep 3; 
        clear; conexiones.sh ; date; diskmax.sh; sleep 3; 
        clear; conexiones.sh ; date; diskmax.sh; sleep 3; 
        clear; conexiones.sh ; date; diskmax.sh; sleep 3;
done
echo "20 loops terminados. Vuela a arrancar: $_ "
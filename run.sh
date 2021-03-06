#!/bin/bash
 if [ -z "$VCAP_APP_PORT" ];
 then SERVER_PORT=80;
 else SERVER_PORT="$VCAP_APP_PORT";
 fi
 echo port is $SERVER_PORT
 python manage.py makemigrations 
 python manage.py migrate 
 python manage.py shell < initdbadmin.py 
 
 echo [$0] Starting Django Server...
 python manage.py runserver 0.0.0.0:$SERVER_PORT --noreload 
 
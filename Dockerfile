FROM overv/openstreetmap-tile-server


RUN sed -i 's/\/tile/.\/tile/g' /var/www/html/index.html
RUN mkdir -p /src && apt-get update && apt-get install -y python3 python3-pip git-lfs curl git ssh wget && apt-get clean
COPY . /src/
RUN cd /src \
 && rm *.ftxt \
 && wget -O ch.ftxt https://github.com/saildeep/ch-renderer/blob/master/ch-bremen.ftxt?raw=true \
 && pip3 install -r requirements.txt \
 && python3 main.py \
 && cp mapnik.xml /home/renderer/src/openstreetmap-carto/mapnik.xml \
 && cp *.geojson /home/renderer/src/openstreetmap-carto/ \
 && rm *.geojson \
 && rm *.ftxt

EXPOSE 80
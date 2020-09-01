FROM overv/openstreetmap-tile-server
RUN apt-get install -y python3.8
RUN mkdir -p /shapedata \
 && cd /shapedata \
 && wget https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json \
 && mv countries.geo.json /data.geojson
RUN sed -i 's/\/tile/.\/tile/g' /var/www/html/index.html
COPY ./mapnik.xml /home/renderer/src/openstreetmap-carto/mapnik.xml
# COPY ./data.geojson /data.geojson

# RUN chown renderer /data.geojson
EXPOSE 80
FROM overv/openstreetmap-tile-server


RUN sed -i 's/\/tile/.\/tile/g' /var/www/html/index.html
RUN mkdir -p /src && apt-get update && apt-get install -y python3 python3-pip git-lfs curl git ssh && apt-get clean
COPY . /src/
RUN cd /src \
 && git remote set-url origin https://github.com/saildeep/ch-renderer.git
 && git lfs pull \
 && pip3 install -r requirements.txt \
 && python3 main.py \
 && cp mapnik.xml /home/renderer/src/openstreetmap-carto/mapnik.xml \
 && cp *.geojson /home/renderer/src/openstreetmap-carto/

EXPOSE 80
FROM overv/openstreetmap-tile-server


RUN sed -i 's/\/tile/.\/tile/g' /var/www/html/index.html
RUN mkdir -p /src && apt-get install -y python3 python3-pip
COPY . /src/
RUN cd /src && pip install -r requirements.txt && python main.py
#COPY ./mapnik.xml /home/renderer/src/openstreetmap-carto/mapnik.xml

EXPOSE 80
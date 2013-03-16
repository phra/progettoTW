#!/bin/bash
echo "aggiorniamo i file da http://vitali.web.cs.unibo.it/TechWeb12/DataSource2/"
rm -rf json/*.json
wget -O json/super.json http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/DataSource2/supermarketBO2011.json
rm -rf csv/*.csv
wget -O csv/scuolematerneBO2011.csv http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/DataSource2/scuolematerneBO2011.csv
rm -rf xml/*.xml
wget -O xml/farma.xml http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/DataSource2/farmacieBO2011.xml
rm -rf rdf/*.ttl
wget -O rdf/posteBO2011.ttl http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/DataSource2/posteBO2011.ttl
echo "fatto!"

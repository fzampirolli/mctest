# decompressed
base64 -d zip.tar.gz.b64 > zip.tar.gz
mkdir zip
mv zip.tar.gz zip
cd zip
tar -xf zip.tar.gz
rm zip.tar.gz

# comentei a linha 19 de vpl_execution.sh

# compressed - in folder zip
tar -czvf zip.tar.gz * && mv zip.tar.gz ../ && cd ../ && rm -rf zip && rm zip.tar.gz
base64 zip.tar.gz > zip.tar.gz.b64

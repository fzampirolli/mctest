# decompressed
base64 -d zip.tar.gz.b64 > zip.tar.gz
tar -xf zip.tar.gz

# comentei a linha 19 de vpl_execution.sh

# compressed
cd zip && tar -czvf zip.tar.gz * && mv zip.tar.gz ../ && cd ../
base64 zip.tar.gz > zip.tar.gz.b64
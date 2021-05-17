# decompressed
base64 -d zip.tar.gz.b64 > zip.tar.gz
mkdir zip
mv zip.tar.gz zip
cd zip
tar -xf zip.tar.gz
rm zip.tar.gz

# compressed - in folder zip
tar -czvf zip.tar.gz * && mv zip.tar.gz ../ && cd ../ && rm -rf zip
base64 zip.tar.gz > zip.tar.gz.b64
rm zip.tar.gz


# comentei a linha 19 de vpl_execution.sh

# 4/5/21 - inclusão de extensões javascript e Rscript

for file in *.tar.gz
do tar -xzvf $file --xform="s|^|$file-|S"
done
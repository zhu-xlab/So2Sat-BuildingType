for pdf in $(ls *pdf)
do
    filename=$(basename $pdf .pdf)
    convert -density 300 $pdf -resize 25% png/$filename.png
done

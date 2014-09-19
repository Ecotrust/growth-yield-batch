for i in *.pdf; do
    convert -density 300 $i $i.png 
done

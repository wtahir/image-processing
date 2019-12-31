
task=signatures
which_dataset=5
nr_ims=50

mkdir /home/diede/$task/
rm -rf /home/diede/$task/$which_dataset/
mkdir /home/diede/$task/$which_dataset/
mkdir /home/diede/$task/$which_dataset/full
mkdir /home/diede/$task/$which_dataset/cropped

echo "filename,class" > /home/diede/$task/$which_dataset/cropped.csv

if [ "$task" == "sketch" ];then
    listfilepath=~/code/data-handmade-sketches/sketch.lst
    entity='sketch'

    locs[0]='centre'
    locs[1]='none'
    classes[0]='Present'
    classes[1]='None'

else
    listfilepath=~/code/data-signature-verification/sig.lst
    entity='signatures2'

    locs[0]='left'
    locs[1]='right'
    locs[2]='left_right'
    locs[3]='none'

    classes[0]='SignatureA'
    classes[1]='SignatureB'
    classes[2]='Both'
    classes[3]='None'
fi

nr_locs=`expr ${#locs[@]} - 1`

function blend_per_position_and_crop {
    # $1 = scanner
    # $2 = form

    mkdir /home/diede/$task/$which_dataset/full/$1/$2
    mkdir /home/diede/$task/$which_dataset/cropped/$1/$2

    jpg=~/code/data-european-accident-statement/empty_forms/$1/extended_region_training_data/$2.jpg
    xml=~/code/data-european-accident-statement/empty_forms/$1/extended_region_training_data/$2.xml
    cp $jpg /home/diede/$task/$which_dataset/full/$1/$2
    cp $xml /home/diede/$task/$which_dataset/full/$1/$2

    find /home/diede/$task/$which_dataset/full/$1/$2 -name "*.xml" > /home/diede/$task/$which_dataset/full/$1/$2/xml.lst
    for i in $(seq 0 $nr_locs)
    do
        class=${classes[$i]}
        if [ "$task" == "sketch" ];then
            python ~/code/image-processing/imageprocessing/image_blend.py /home/diede/$task/$which_dataset/full/$1/$2/xml.lst $listfilepath ${locs[$i]} $nr_ims /home/diede/$task/$which_dataset/full/$1/$2 --xpath '//*[_:Property[@key="entity" and starts-with(@value, "'$task'")]]'
        else
            python ~/code/image-processing/imageprocessing/image_blend.py /home/diede/$task/$which_dataset/full/$1/$2/xml.lst $listfilepath ${locs[$i]} $nr_ims /home/diede/$task/$which_dataset/full/$1/$2 --xpath '//*[_:Property[@key="entity" and starts-with(@value, "'$task'2")]]'
        fi

        for f in /home/diede/$task/$which_dataset/full/$1/$2/${locs[$i]}*.png
        do
            echo '       ' $(basename $f)
            python ~/code/image-processing/imageprocessing/image_tools.py crop_region /home/diede/$task/$which_dataset/full/$1/$2/$2.xml $entity /home/diede/$task/$which_dataset/cropped/$1/$2/$(basename $f) $(basename $f)
            echo "$1/$2/$(basename $f)"",""$class"
            echo "$1/$2/$(basename $f)"",""$class" >> /home/diede/$task/$which_dataset/cropped.csv
        done
    done
    rm -rf /home/diede/$task/$which_dataset/full/$1/$2
}

export -f blend_per_position_and_crop

for scanner in 'Huawei-Mate-10-Pro' 'Huawei-Y7' 'Sharp-MX-2630N'
do
    mkdir /home/diede/$task/$which_dataset/full/$scanner
    mkdir /home/diede/$task/$which_dataset/cropped/$scanner
    for form in 'dutch_1' 'dutch_3' 'french-english_1'
    do
        echo $scanner
        echo $form
        blend_per_position_and_crop $scanner $form &
    done
done



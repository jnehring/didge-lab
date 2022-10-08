DidgeLab to Blender Converter

open didge

PROD_DIR=/home/jan/workspaces/didge-sound/production
python convert_to_blender.py -infile $PROD_DIR/open_didge/didgelab/0_geo.txt -outfolder $PROD_DIR/open_didge/blender -outer_bubbles 430 10 60 1220 10 60

# create inner and outer shape
```
PROD_DIR=/home/jan/workspaces/didge-sound/production

python convert_to_blender.py -infile $PROD_DIR/arusha_1/didgelab/0_geo.txt -outfolder $PROD_DIR/arusha_1/blender -thickness 3 -inner_resolution 3 -outer_resolution 3 -wn 0.01 -outer_bubbles 830 10 60 1486 20 60

python convert_to_blender.py -infile $PROD_DIR/kizimkazi_1/didgelab/0_geo.txt -outfolder $PROD_DIR/kizimkazi_1/didgelab -no_smooth

python convert_to_blender.py -infile $PROD_DIR/matema_1/0_geo.txt -outfolder $PROD_DIR/matema_1/ -wn 0.01 
python convert_to_blender.py -infile $PROD_DIR/mbeya_1/didgelab/0_geo.txt -outfolder $PROD_DIR/mbeya_1/didgelab/
python convert_to_blender.py -infile $PROD_DIR/mbeya_2/0_geo.txt -outfolder $PROD_DIR/mbeya_2/ -no_smooth 
python convert_to_blender.py -infile $PROD_DIR/open_didge/didgelab/0_geo.txt -outfolder $PROD_DIR/open_didge/didgelab/
```



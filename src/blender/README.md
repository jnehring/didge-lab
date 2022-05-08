DidgeLab to Blender Converter

# create inner and outer shape
```
PROD_DIR=/home/jan/workspaces/didge-sound/production

python convert_to_blender.py -infile $PROD_DIR/arusha_1/0_geo.txt -outfolder $PROD_DIR/arusha_1/ -wn 0.01 
python convert_to_blender.py -infile $PROD_DIR/kizimkazi_1/0_geo.txt -outfolder $PROD_DIR/kizimkazi_1/ -wn 0.01 -no_smooth 
python convert_to_blender.py -infile $PROD_DIR/matema_1/0_geo.txt -outfolder $PROD_DIR/matema_1/ -wn 0.01 
python convert_to_blender.py -infile $PROD_DIR/mbeya_1/didgelab/0_geo.txt -outfolder $PROD_DIR/mbeya_1/didgelab/
python convert_to_blender.py -infile $PROD_DIR/mbeya_2/0_geo.txt -outfolder $PROD_DIR/mbeya_2/ -no_smooth 
python convert_to_blender.py -infile $PROD_DIR/open_didge/didgelab/0_geo.txt -outfolder $PROD_DIR/open_didge/didgelab/
```



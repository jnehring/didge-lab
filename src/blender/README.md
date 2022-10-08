# DidgeLab to Blender Converter

```
usage: convert_to_blender.py [-h] -infile INFILE
                             [-inner_resolution INNER_RESOLUTION]
                             [-outer_resolution OUTER_RESOLUTION]
                             [-thickness THICKNESS] [-outfolder OUTFOLDER]
                             [-wn WN] [-inner_only] [-no_mouthpiece]
                             [-no_smooth]
                             [-outer_bubbles OUTER_BUBBLES [OUTER_BUBBLES ...]]

Create outer shape to a didgelab geometry with smoothing.

optional arguments:
  -h, --help            show this help message and exit
  -infile INFILE
  -inner_resolution INNER_RESOLUTION
                        Put an inner segment every resolution mm. default=5
  -outer_resolution OUTER_RESOLUTION
                        Put an outer segment every resolution mm. default=10
  -thickness THICKNESS  Wall thickness in mm. default=5.
  -outfolder OUTFOLDER
  -wn WN                butterdingens. default=0.1
  -inner_only           necessary inner rings only
  -no_mouthpiece        do not add the mouthpiece
  -no_smooth            skip smoothing
  -outer_bubbles OUTER_BUBBLES [OUTER_BUBBLES ...]
                        add bubbles to outer shape in format pos, height,
                        width

```

```
PROD_DIR=/home/jan/workspaces/didge-sound/production
python convert_to_blender.py -infile $PROD_DIR/open_didge/didgelab/0_geo.txt -outfolder $PROD_DIR/open_didge/blender -outer_bubbles 430 10 60 1220 10 60
```

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



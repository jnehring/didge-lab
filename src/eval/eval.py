'''
 set
export CADSD_BACKEND=python
'''
import json
import os
from .didge import do_fft, comparison_plot

archive_path_json = "../../didge-archive/didge-archive.json"

archive_path = os.path.dirname(archive_path_json)
archive = json.load(open(archive_path_json, "r"))

didge = archive[1]

geo = json.load(open(os.path.join(archive_path, didge["geometry"]), "r"))
audio_file = os.path.join(archive_path, didge["audio-samples"]["neutral-sound"])
# comparison_plot(audio_file, geo, didge_name=didge["name"])



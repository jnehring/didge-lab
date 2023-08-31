'''
 set
export CADSD_BACKEND=python
'''
import json
import os
from .diff import ground_spectrum_difference

archive_path_json = "../../didge-archive/didge-archive.json"

archive_path = os.path.dirname(archive_path_json)
archive = json.load(open(archive_path_json, "r"))

didge = archive[1]

geo = json.load(open(os.path.join(archive_path, archive[1]["geometry"]), "r"))
audio_file = os.path.join(archive_path, didge["audio-samples"]["neutral-sound"])

diff = ground_spectrum_difference(audio_file, geo)
print(diff)
# comparison_plot(audio_file, geo, didge_name=didge["name"])



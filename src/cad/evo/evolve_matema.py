# matema has two very strong peaks in the ground tone spektrum that play a chord

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MatemaShape
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss, ImpedanceVolumeLoss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSD, cadsd_octave_tonal_balance
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
from cad.ui.evolution_ui import EvolutionUI
from cad.calc.util.losslog import LossLog
from cad.calc.util.cad_logger import LossCADLogger
import logging
import sys
import json

class MatemaLoss(LossFunction):

    def __init__(self):
        LossFunction.__init__(self)
        self.base_note=-31

        self.target_peaks=[
            73.416192,      # base note - D
            698.4564628660078/2,
            880.0
        ]

        scale=[0,3,7,10]
        freq=note_to_freq(self.base_note)
        self.scale_peaks=[freq]
        i=0
        while freq<1000:
            oct=np.floor(i/len(scale))
            note=self.base_note + oct*12 + scale[i%len(scale)]
            freq=note_to_freq(note)
            #print(i, oct*12, scale[i%len(scale), note)
            i+=1
            self.scale_peaks.append(math.log(freq, 2))
        

    def get_loss(self, geo, context=None):

        fundamental=geo.get_cadsd().get_notes().iloc[0].freq
        fundamental_loss=pow(abs(fundamental-note_to_freq(self.base_note)), 10)

        peaks=geo.get_cadsd().get_notes().copy()

        singer_tuning_loss=0
        singer_volume_loss=0
        for target_freq in self.target_peaks:
            peaks["diff"]=abs(peaks.freq-target_freq)
            closest_peak=peaks[peaks["diff"]==peaks["diff"].min()].iloc[0]

            f1=math.log(target_freq, 2)
            f2=math.log(closest_peak["freq"], 2)
            singer_tuning_loss += math.sqrt(abs(f1-f2))

            singer_volume_loss += math.sqrt(1/(closest_peak["impedance"]/1e6))
        singer_tuning_loss*=4

        # tune all other overtones
        toot_tuning_loss=0
        notes=geo.get_cadsd().get_notes()
        notes=notes[notes.rel_imp>0.15]
        for ix, note in notes.iterrows():
            f1=math.log(note["freq"], 2)
            f2=min(self.scale_peaks, key=lambda x:abs(x-f1))
            toot_tuning_loss += math.sqrt(abs(f1-f2))
        toot_tuning_loss*=3
        #volume_loss/=10

        losses={
            "toot_tuning_loss": toot_tuning_loss,
            "singer_tuning_loss": singer_tuning_loss,
            "singer_volume_loss": singer_volume_loss,
            "fundamental_loss": fundamental_loss
        }
        final_loss=sum(losses.values())
        losses["loss"]=final_loss
        return losses

if __name__=="__main__":
    try:
        App.full_init("evolve_matema")

        # geo=[[0, 32], [10.0, 31.973272889019487], [37.27272727272727, 31.90038076816354], [64.54545454545455, 31.82748864730759], [91.81818181818181, 31.754596526451643], [100.63483066273089, 31.73137523235442], [119.0909090909091, 31.681704405595696], [146.36363636363637, 31.60881228473975], [173.63636363636363, 31.5359201638838], [200.9090909090909, 31.463028043027855], [208.096034355497, 31.676731530059175], [220.57489071628004, 31.982912006908304], [228.1818181818182, 31.390135922171904], [255.45454545454547, 31.317243801315957], [282.72727272727275, 31.24435168046001], [310.0, 31.171459559604063], [395.88009205356195, 31.244532609752895], [439.7959582917049, 31.161576127451113], [478.40521303767895, 31.08864376308305], [487.65642963539665, 31.036567856444652], [562.1941098954468, 30.867665820300225], [624.7952879660339, 30.725811842496345], [662.5194724402834, 31.463406515802237], [699.1998428592318, 32.10274615046516], [709.7663791454306, 31.39002492993869], [718.6912342898563, 30.788036399424186], [729.6346035426079, 30.04989749758933], [740.2196792588061, 32.072515291252614], [741.2559423549741, 32.118633669647984], [754.4124927836987, 33.50567303911912], [766.5972084060718, 34.7360576678699], [782.5599821235987, 36.34794193525562], [808.3418460452156, 36.978952771914244], [809.7407775938035, 37.02592790277677], [815.4181131125595, 37.24941523271939], [837.6019260461422, 38.128623624729784], [868.6548991615795, 39.35764620672749], [871.6684545520726, 40.54537225578667], [877.8256635693822, 42.9720996895784], [924.1131705007213, 44.269021531434916], [952.1237137076439, 45.05384421244926], [977.3974500700557, 46.66305007444131], [996.4165273258797, 47.87401509246965], [1019.475166028975, 49.677741860461154], [1043.8059659021726, 51.58098149151708], [1047.1868750285528, 52.00953278520254], [1066.1735200313528, 52.72682429273316], [1092.7144219524905, 53.72950610131113], [1112.15567627516, 53.93560645247775], [1122.2927072921639, 53.95984029024736], [1123.508019929061, 54.149695043608936], [1138.300296175778, 55.9690408548472], [1166.130808041641, 57.09806679737621], [1192.973831042207, 58.18703237190866], [1218.5834829598994, 59.45790036561972], [1245.1765196431754, 60.60312180781659], [1248.6452091079618, 60.764290201189255], [1282.6735410338385, 62.24305648128914], [1311.8137679335068, 63.50940080364836], [1345.939157882664, 64.05381098736974], [1388.840913088351, 65.80715400297], [1408.9568536777442, 66.62926824434645], [1459.6465719290761, 68.70089592094405], [1495.1402128194193, 70.72010874320598], [1559.3926194585617, 74.37539121331861], [1578.17109537064, 75.89616298585814], [1636.0445956655017, 75.91007049669538], [1643.2705763237045, 78.36586468557032], [1692.8764937166407, 77.51160163745824], [1700.9538546793087, 79.56415578973488], [1712.8764935839176, 82.51160160464723], [1712.8764937166407, 82.51160163745824]]
        # geo=Geo(geo)

        losslogger=LossCADLogger()

        loss=MatemaLoss()    

        shape=MatemaShape(n_bubbles=2, add_bubble_prob=0.4)

        ol=1847.567267735626
        ol-=30 # die reflektion entsteht nach ca 1/3 des belldurchmessers
        shape.set_minmax("length", ol, ol)
        shape.set("length", ol)

        # shape.set_minmax("opening_factor_y", 1.5, 2.0)
        # shape.set_minmax("d_pre_bell", 0, 10)
        # shape.set_minmax("bellsize", 3, 20)

        initial_pool=MutantPool.create_from_father(shape, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=100, generation_size=30))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=50, generation_size=30))

        for i in range(2):
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)

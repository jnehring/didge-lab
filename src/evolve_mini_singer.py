from cad.calc.pipeline import Pipeline, ExplorePipelineStep, FinetuningPipelineStep
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.didgedb import DidgeMongoDb, DatabaseObject
from cad.calc.parameters import MutationParameterSet
from cad.calc.loss import Loss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSDResult
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo

App.init_logging()

class RandomDidgeParameters(MutationParameterSet):
    
    def __init__(self):
        MutationParameterSet.__init__(self)
        
        self.add_param("length", 1000, 1700)
        self.add_param("bell_width", 50, 300)
        self.add_param("n_segments", 2, 20)
        self.add_param("first_segment", 0.2, 0.8)
        self.add_param("d1", 0,0, value=32, immutable=True)
    
    def after_mutate(self):
        self.get("n_segments").toint()
        
    def make_geo(self):
        self.get("n_segments").toint()

        shape=[
            [0, self.get("d1").value]
        ]

        y=np.random.sample(self.get_value("n_segments"))

        target_width=self.get_value("bell_width")-self.get_value("d1")
        y=y/y.sum()
        offset=0
        for i in range(len(y)):
            y[i]+=offset
            offset=y[i]
        y*=target_width
        y+=self.get_value("d1")

        x=np.random.sample(self.get_value("n_segments")-1)
        x=x/x.sum()
        x*=(1-self.get_value("first_segment"))
        x=np.concatenate([[self.get_value("first_segment")], x])
        x*=self.get_value("length")

        offset=0
        for i in range(len(x)):
            x[i]+=offset
            offset=x[i]

        for i in range(len(x)):
            shape.append([x[i], y[i]])

        return Geo(geo=shape)
                           
    def after_mutate(self):
        self.get("n_segments").toint()

father=RandomDidgeParameters()
father.set_minmax("length", 1300, 1700)
father.set_minmax("bell_width", 50, 100)
initial_pool=MutantPool.create_from_father(father, App.get_config().n_poolsize)

class SingerLoss(Loss):

    def __init__(self):
        Loss.__init__(self)

    def loss_per_frequency(self, f1, f2):
        f1=math.log(f1, 2)
        f2=math.log(f2, 2)
        return abs(f1-f2)

    def get_loss(self, geo, peaks=None, fft=None):
        
        base_note=-31 # should be a D
        res=CADSDResult.from_geo(geo)
        peaks=res.peaks

        freqs=list(peaks.freq)

        # tune base note

        fundamental=-31
        base_freq=note_to_freq(-31)
        base_note_loss=self.loss_per_frequency(base_freq, freqs[0])

        # tune overtones
        overtone_loss=0
        
        scale=np.array([0,2,3,5,7,9,10])+fundamental
        scale_frequencies=[]
        for i in range(len(scale)):
            for octave in range(5):
                scale_frequencies.append(note_to_freq(scale[i] + 12*octave))

        for i in range(1, len(freqs)):
            freq=freqs[i]
            f_next_scale=min(scale_frequencies, key=lambda x:abs(x-freq))
            l = self.loss_per_frequency(freq, f_next_scale)
            overtone_loss+=l
        overtone_loss /= len(freqs)-1

        # singer loss
        singer_loss=1-(peaks[peaks.freq>=500].impedance.sum()/peaks.impedance.sum())
        singer_loss=max(0, singer_loss-0.2)

        final_loss=base_note_loss+overtone_loss+singer_loss
        return final_loss, res

loss=SingerLoss()
pipeline=Pipeline("minisinger")
pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool))
pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss))
pipeline.run()
# l=[]
# d=[]
# for i in range(0, 20):
#     m.mutate(p)
#     p.after_mutate()  
#     geo=p.make_geo()
#     l.append(geo.length())
#     d.append(geo.geo[-1][1])
# print("length")
# print(f"mean: {np.mean(l):.2f}")
# print(f"min: {np.min(l):.2f}")
# print(f"max: {np.max(l):.2f}")

# print("bell")
# print(f"mean: {np.mean(d):.2f}")
# print(f"min: {np.min(d):.2f}")
# print(f"max: {np.max(d):.2f}")

# #class MiniSingerLoss():


# #class SearchInDbStep(PipelineStep):

#     # def __init__(self):
#     #     super().__init__("SearchInDb")

#     # def execute(self, pool : MutantPool ) -> MutantPool:
#     #     poolsize=App.get_config().n_poolsize
#     #     db=DidgeMongoDb()
#     #     fundamental=-31
#     #     loss=ScaleLoss(scale=[0,3,5,7,10], fundamental=fundamental, n_peaks=8, octave=True)

#     #     c=0

#     #     target_notes=[fundamental, fundamental+12, fundamental+24, fundamental-12]
#     #     pool=[]
        
#     #     #f={"parameterset": "<class '__main__.RoundedDidge'>"}
#     #     f={"base_note": "D1"}
#     #     total=db.get_collection().count_documents(filter=f)
#     #     pbar=tqdm(total=total)

#     #     early_stop=-1
#     #     for o in db.get_collection().find(f):
#     #         c+=1

#     #         if c==early_stop:
#     #             break

#     #         count=0
#     #         pbar.update(1)

#     #         for p in o["peak"][0:2]:

#     #             if p["note-number"] in target_notes:
#     #                 count+=1
#     #         if count<2:
#     #             continue

#     #         do=DatabaseObject.from_json(o)
#     #         geoloss=loss.get_loss(do.geo, peaks=do.peak)
#     #         pool.append((do, geoloss))

#     #         pool=sorted(pool, key=lambda x : x[1])
#     #         if len(pool)>poolsize:
#     #             pool=pool[0:poolsize]

#     #     pool=MutantPool(pool=pool)
#     #     return pool

    
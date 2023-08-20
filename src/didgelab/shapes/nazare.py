from didgelab.calc.geo import Geo, geotools
from didgelab.calc.conv import note_to_freq
from didgelab.shapes.util import scale

from didgelab.evo.loss import LossFunction
from didgelab.evo.parameters import MutationParameterSet

class NazareLoss(LossFunction):
        
    def __init__(self):
        LossFunction.__init__(self)
        
        base_note = -31
        self.target_notes = np.array([0,16,24])+base_note
        self.target_freqs = np.log2(note_to_freq(self.target_notes))

        opendidge = [[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
        self.base_brightness = self.get_brightness(Geo(opendidge))
        # self.multiples = np.arange(1,15)*note_to_freq(base_note)

    def get_brightness(self, geo):
        return geo.get_cadsd().get_impedance_spektrum().query("freq>=400 and freq<=800").impedance.sum()

    def get_deviations(self, freq, reference):
        
        deviations = []
        for f in freq:
            d = [np.abs(r-f) for r in reference]
            deviations.append(np.min(d))
        return deviations
        
    def get_loss(self, geo, context=None):
        
        notes = geo.get_cadsd().get_notes()
        freqs = np.log2(list(notes.freq))
        toots = freqs[0:3]
        others = freqs[3:]
        
        deviations = self.get_deviations(toots, self.target_freqs)
        fundamental_loss = deviations[0]
        fundamental_loss *= 30
        toots_loss = np.sum(deviations[1:])/2
        toots_loss *= 10

        brightness_loss = self.base_brightness / self.get_brightness(geo)
        brightness_loss *= 10
        
        loss = {
            "loss": fundamental_loss + toots_loss + brightness_loss,
            "fundamental_loss": fundamental_loss,
            "toots_loss": toots_loss,
            "brightness_loss": brightness_loss
        }
        return loss
    
class NazareShape(MutationParameterSet):
    
    def __init__(self):
        
        MutationParameterSet.__init__(self)

        self.d1=32
        self.n_segments = 10
        
        self.add_param("length", 1450, 1600)
        self.add_param("bellsize", 65, 80)
        self.add_param("power", 1,2)
        
        self.add_param("widening_1_x", 500, 800)
        self.add_param("widening_1_y", 1.0, 1.3)
        self.add_param("widening_2_x", 800, 1400)
        self.add_param("widening_2_y", 1.0, 1.3)
        
        self.n_bubbles=1
        self.n_bubble_segments=10
        for i in range(self.n_bubbles):
            self.add_param(f"bubble{i}_width", 100, 200)
            self.add_param(f"bubble{i}_height", 0, 15)
            self.add_param(f"bubble{i}_pos", -0.3, 0.3)
        
    def make_geo(self):
        length = self.get_value("length")
        bellsize = self.get_value("bellsize")

        x = length*np.arange(self.n_segments+1)/self.n_segments
        y= np.arange(self.n_segments+1)/self.n_segments
        
        
        p = self.get_value("power")
        y = np.power(y, p)
        y = np.power(y, p)
        y = np.power(y, p)
        y = self.d1 + y*(bellsize - self.d1)
        
        widenings = [[self.get_value(f"widening_{i}_x"), self.get_value(f"widening_{i}_y")] for i in range(1,3)]
        for w in widenings:
            geo = list(zip(x,y))
            d=geotools.diameter_at_x(Geo(geo), w[0])
            
            add_d = w[1]*d - d
            for i in range(len(geo)):
                if geo[i][0] >= w[0]:
                    break
            
            x = np.concatenate((x[0:i], [w[0]], x[i:]))
            y_right = np.concatenate(([d], y[i:])) + add_d
            y = np.concatenate((y[0:i], y_right))
        
            y[i:] /= y[-1]/bellsize
            
        shape = list(zip(x,y))
        
        bubble_length = length-100

        for i in range(self.n_bubbles):
            
            width = self.get_value(f"bubble{i}_width")
            height = self.get_value(f"bubble{i}_height")
            pos = self.get_value(f"bubble{i}_pos")
                
            x = width * np.arange(self.n_bubble_segments)/self.n_bubble_segments
            y = height * np.sin(np.arange(self.n_bubble_segments)*np.pi/self.n_bubble_segments)
            
            x += bubble_length * i/self.n_bubbles
            x += (0.5+pos)*bubble_length/self.n_bubbles
                        
            if x[0] < 0:
                x += -1*x[0]
                x += 1
            if x[-1] > bubble_length:
                x -= x[-1] - (bubble_length)
            
            geo = Geo(shape)
            y += np.array([geotools.diameter_at_x(geo, _x) for _x in x])
            
            shape = list(filter(lambda a : a[0]<x[0] or a[0]>x[-1], shape))
            shape.extend(zip(x,y))
            shape = sorted(shape, key=lambda x : x[0])
        
        return Geo(shape)
    
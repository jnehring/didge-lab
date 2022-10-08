import torch
from torch.nn import MSELoss
from cad.cadsd.pytorch.cadsd_pytorch import Segment, cadsd_Ze
import matplotlib.pyplot as plt
import numpy as np
import torch.optim as optim

fmin=30
fmax=400

class DidgeModel(torch.nn.Module):

    def __init__(self):
        torch.nn.Module.__init__(self)

        self.length=torch.nn.Parameter(torch.tensor([120.0]))
        self.d0=32
        # self.d1=torch.tensor([32])
        self.d1=torch.nn.Parameter(torch.tensor([80.0]))
        
    def get_segments(self):
        seg1=torch.tensor([0, self.d0])
        seg2=torch.cat((self.length*10, self.d1))
        segments=torch.stack((seg1, seg2))
        segments=Segment.create_segments_from_geo(segments)
        return segments

    def forward(self, fmin, fmax):

        segments=self.get_segments()
        impedances=[]
        for f in range(fmin, fmax):
            impedances.append(cadsd_Ze(segments, f))
        return torch.stack(impedances)

class TestModel2(torch.nn.Module):
    def __init__(self):
        torch.nn.Module.__init__(self)

        self.x=torch.nn.Parameter(torch.tensor([30.0]))
        self.y=torch.nn.Parameter(torch.tensor([50.0]))
        
    def forward(self):

        target_freqs=torch.concat((self.x, self.y))
        width=torch.tensor(10)

        x=torch.tensor(np.arange(fmin, fmax))
        y=[]
        for _x in x:

            f=(target_freqs-_x).argmin().detach()
            f=target_freqs[f]
            d=torch.pow(_x-f, 2)
            if d>width:
                y.append(torch.tensor(0, dtype=torch.double))
            else:
                y.append(torch.pow(width-d, 2))

        y=torch.stack(y)
        target_y=y/y.max()
        return target_y

class TestModel(torch.nn.Module):
    def __init__(self):
        torch.nn.Module.__init__(self)

        self.length=torch.nn.Parameter(torch.tensor([1800.0]))
        self.d0=32
        self.d1=torch.nn.Parameter(torch.tensor([80.0]))

    def get_segments(self):

        segments=torch.tensor([
            [0, self.d0],
            [self.length, self.d1]
        ], requires_grad=True)
        segments=Segment.create_segments_from_geo(segments)
        return segments
        
    def forward(self):
        segments=self.get_segments()

        target_freqs=torch.concat((self.x, self.y))
        width=torch.tensor(10)

        x=torch.tensor(np.arange(fmin, fmax))
        y=[]
        for _x in x:

            f=(target_freqs-_x).argmin().detach()
            f=target_freqs[f]
            d=torch.pow(_x-f, 2)
            if d>width:
                y.append(torch.tensor(0, dtype=torch.double))
            else:
                y.append(torch.pow(width-d, 2))

        y=torch.stack(y)
        target_y=y/y.max()
        return target_y

def plot_model(model):
    segments=model.get_segments()
    impedances=[]
    x=[]
    for f in range(fmin, fmax):
        x.append(f)
        impedances.append(cadsd_Ze(segments, f).detach())
    impedances=np.array(impedances)
    impedances=impedances/impedances.max()
    return x, impedances


def train():

    f0=73
    target_freqs=[f0]
    width=10

    x=np.arange(fmin, fmax)
    y=[]
    for _x in x:
        f=np.argmin([np.abs(f-_x) for f in target_freqs])
        f=target_freqs[f]
        d=np.abs(_x-f)
        if d>width:
            y.append(0)
        else:
            y.append(np.power(width-d, 2))
    y=np.array(y)
    target_y=torch.tensor(y/y.max())

    # mini=np.array(argrelextrema(target_y.numpy(), np.greater))+fmin

    model=DidgeModel()

    # x,y=plot_model(model)
    # plt.plot(x,y)

    # model=TestModel2()

    criterion = MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=100, momentum=0.9)

    
    plt.ion()

    x,y=plot_model(model)
    plt.plot(x,target_y)
    plt.plot(x,y)
    plt.draw()
    plt.clf()

    for i in range(2000):
        optimizer.zero_grad()

        outputs = model(fmin, f0+width)
        outputs=outputs/outputs.max()

        region=np.arange(fmin, f0+width)
        region-=fmin

        # plot computational graph
        # dot = make_dot(outputs, params=dict(model.named_parameters()), show_attrs=True, show_saved=True) 
        # dot.render("test.png")

        loss = criterion(outputs, target_y[region])
        loss.backward()
        optimizer.step()

        if i%50==0:
            print(i, "loss", loss.item())
            print(list(model.parameters()))

            plt.clf()
            x,y=plot_model(model)
            plt.plot(x,target_y)
            plt.plot(x,y)
            plt.draw()




    # # for local maxima
    # x,y=plot_model(model)
    # plt.plot(x,y)

    # mini=np.array(argrelextrema(y, np.greater))+fmin
    # print(mini)


    # plt.plot(x,target_y)


    # plt.plot(x, impedances)
    # plt.show()



    # inputs, labels = data

    # # zero the parameter gradients
    # optimizer.zero_grad()

    # # forward + backward + optimize
    # outputs = net(inputs)
    # loss = criterion(outputs, labels)
    # loss.backward()
    # optimizer.step()


    


if __name__=="__main__":

    train()

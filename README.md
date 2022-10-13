# DidgeLab

## 1. Introduction
DidgeLab is a free toolkit to compute didgeridoo shapes. Traditionally, building a didgeridoo is a random process. Builders know how a shape influences the sound, but the exact sonic properties of the didgeridoo can only be determined after it was built. The DidgeLab software helps Didgeridoo builders to define a sound, compute the shape of the didgeridoo and then build it according to that shape.

It mainly can do two things:

1. Acoustical simulation to compute resonant frequencies of a didgeridoo shape. This functionality is very similar to [Didgmo](https://sourceforge.net/projects/didgmo/) and [DidjiImp](https://sourceforge.net/projects/didjimp/).
2. Computational evolution to find didgeridoo shapes with certain sonic properties. This functionality is inspired by the works of [Frank Geipel](https://www.didgeridoo-physik.de/).

So the first functionality takes a didgeridoo shape as in input and computes its sonic properties. The 2nd functionality works vice versa: It takes sonic properties as an input and generates a didgeridoo shape with these sonic capabilities. Especially the 2nd functionality is super interesting. To the best of my knowledge, DidgeLab is the first open toolkit to implement this functionality.

Unfortunately the software is complicated to use. It is a command line application, which means: There is no graphical user interface. When you use the software you most likely need to program in python, because it is more of a python programming toolkit than a normal end user software.

## 2. Related works

DidgeLab stands on the shoulders of giants:

* Most important, the [pioneering works of Frank Geipel]((https://www.didgeridoo-physik.de/)) and his Computer-Aided-Dideridoo-Sound-Design-Tools (CADSD). I am not exactly sure what Frank Geipel did. But after reading through his website 1000 times I implemented DidgeLab in the way I understood he implemented it.
* The acoustic simulation of the didgeridoo is based on transmission line modeling, see [Dan Mapes-Riordan, 1991: Horn Modeling with Conical and Cylindrical Transmission Line Elements
](https://www.aes.org/e-lib/browse.cfm?elib=5522).
* There is a lot of important background information on didgeridoo acoustics in [Andrea Ferronis Youtube channel](https://www.youtube.com/), most notably:
  * [DIDGMO - The didgeridoo sound design software. How to set it and how to read the results
](https://www.youtube.com/watch?v=wWRTe3FMCWI&t=1017s)
  * [Acoustic and color tone of cylindrical and conical didgeridoo](https://www.youtube.com/watch?v=idcPw0RaUiE)
  * [Didgeridoo backpressure - Everything you know about it is probably wrong](https://www.youtube.com/watch?v=2q5TCpuf07U)
  Andrea also offers webinars on Didgeridoo per year which are super informative.

## 3. What can it do? Where are practical examples?

Well. Thats the thing. Currently I never built a Didgeridoo with a shape that this software computed. I computed some shapes with interesting sonic properties. I also spent a month in a 3d printing lab but I invested a lot of time in the printer and could not get it to work. After a pause from the 3d printer, I will restart this effort. So meanwhile I release this software as open source.

But the software should be able to do these things:

* You first think of the sound the didgeridoo should produce. And then the software computes a shape with that sound.
* Compute didgeridoos with precisely tuned resonant frequencies. So if you want a Didgeridoo that, for example, has a drone in D and toots in F, G and B, the software can produce a shape with these precisely tuned toots.
* Produce "singing" didgeridoos with super dominant overtones.
* Produce shapes that hardly exist in nature, of that come up very seldomly. Frank Geipel did this with the [Long Multi Tooter](https://www.didgeridoo-physik.de/didge-physics/long-multi-tooter/) but there might be more forms out there.
* And more. You can check out [Frank Geipels](https://www.didgeridoo-physik.de/news-archiv/) blog. With some extensions, DidgeLab should be able to do similar things.

You might ask yourself how I verify that the software works if I never built a didge with it. The Didgmo and Didjimp programs are known to work. If I put didgeridoo geometries computed by DidgeLab into these programs, they produce the same impedance spektra that I computed with DidgeLab. But of course I would love to build some Didgeridoos and it will not take long until I have a better verification.

## 4. Usage

### 4.1 Installation

Up to now it ran solely on Ubuntu linux. It should run in MS Windows and MacOS too, but nobody every tried that.

Prerequisites

* python 3.8 (other python versions will work also, but nobody tried yet)
* we recommend a virtual environment using e.g. pip or conda. In this environment, you install all required python packages with pip:

```
pip install -r requirements.txt
```

To use the didge reporting tool you need to have latex installed. Latex distributions tend to be large, e.g. tex-live is 5 GB. So you can start without Latex and then install it when you want to use the didge-reporting tool. Assuming you are using Ubuntu Linux, use this command. Sorry I did not test this because i have latex already installed. Probably a smaller Latex distribution will work also.

```
apt install texlive-full
```

### 4.2 Documentation

There is a tutorial series how to use the code:

If you use the system and struggle because you need more information, then please open a GitHub issue. I can write more documentation if there is a demand for it.

### 4.3 How to build a didgeridoo after these specifications.

This is out of scope for this document. Again I refer to [Frank Geipels Website](https://www.didgeridoo-physik.de), he wrote down some ideas. I am trying 3d printing but there are other ways to do it.

## 5. Didgeridoo geometry collection

There is a series of didgeridoo geometries with interesting sonic capabilities published as well. If you have a Didgeridoo geometry with interesting sonic properties you can publish it here also.

The Didgeridoo geometries are published in the DidgeLab format

## 6. Get involved

This project is open source. Please use the GitHub issues system for questions, feedback, etc. You can send me a private message on GitHub, but please consider: If the information might be interesting for others, which is especially the case for questions or bug reports, then use the GitHub issues system so others can see this conversation also.

## 7. Licensing / What does it cost?

The software is free and released unter the GNU GPL v2.0 license.


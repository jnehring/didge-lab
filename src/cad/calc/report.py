import pandas as pd
import matplotlib.pyplot as plt
from cad.calc.conv import freq_to_note, note_name
from cad.calc.didgmo import didgmo_bridge
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser
import os

def make_html_report(mutants, dir):

    if not os.path.exists(dir):
        os.mkdir(dir)

    html=open("assets/report_template.html").read()

    html_overview="<table><tr class=\"even\">\n"
    html_overview+='<th>shape</th>\n'
    html_overview+='<th>loss</th>\n</tr>\n'
    for i in range(len(mutants)):
        rclass = "even" if i%2==0 else "odd"
        html_overview += f"<tr><td class=\"{rclass}\">"
        html_overview += f"<a href=\"#{i}\">shape {i}</a></td>"
        loss=mutants[i]["loss"]
        html_overview += f"<td>{loss}</td></tr>\n"

    html_overview+="<table>"
    html=html.replace("$overview$", html_overview)

    content_html=""
    for i_shape in range(len(mutants)):

        geo=mutants[i_shape]["mutant"].make_geo()
        suffix=str(i_shape)
        plt.figure(2*i_shape)
        DidgeVisualizer.vis_didge(geo)
        plt.savefig(os.path.join(dir,'didge' + suffix + '.png'))

        peak, fft=didgmo_bridge(geo)
        plt.figure(2*i_shape+1)
        FFTVisualiser.vis_fft_and_target(fft)
        plt.savefig(os.path.join(dir,'impedance_spektrum' + suffix + '.png'))
        bell_size=geo.geo[-1][1]

        shape_html=open("assets/report_content_template.html").read()
        shape_html = shape_html.replace("$suffix$", suffix)

        dimensions="<table><tr class=\"even\"><th>x</th><th>diameter</th></tr>"
        i=0
        for g in geo.geo:
            i+=1
            rclass = "even" if i%2==0 else "odd"
            dimensions += f"<tr class=\"{rclass}\"><td>{g[0]:.2f}</td><td>{g[1]:.2f}</td></tr>"
        dimensions += "</table>"
        shape_html = shape_html.replace("$dimensions$", dimensions)

        peaks="<table><tr class=\"even\"><th>freq</th><th>note</th><th>cent-diff</th><th>amp</th></tr>"
        i=0
        for p in peak.impedance_peaks:
            i+=1
            freq=p["freq"]
            note=p["note"]
            cdiff=p["cent-diff"]
            amp=p["amp"]
            rclass="even" if i%2==0 else "odd"
            peaks += f"<tr class=\"{rclass}\">"
            peaks += f"<td>{freq}</td>" 
            peaks += f"<td>{note}</td>"  
            peaks += f"<td>{cdiff}</td>"  
            peaks += f"<td>{amp:.2E}</td></tr>"
        peaks += "</table>"
        shape_html = shape_html.replace("$impedance_table$", peaks)
        content_html+=shape_html

    html=html.replace("$report$", content_html)
    report_file=os.path.join(dir, "report.html")
    f=open(report_file, "w")
    f.write(html)
    f.close()

    print("wrote html report to " + report_file)


    # print("size bell end: %.00fmm" % (bell_size))
    # return fft, peak

def geo_report(geo):

    print("-"*20)
    print("properties")
    df={
        "property": [],
        "value": []
    }

    def add_property(name, value):
        df["property"].append(name)
        df["value"].append(value)
    add_property("length", geo.geo[-1][0])
    add_property("bell_size", geo.geo[-1][1])
    df=pd.DataFrame(df)
    print(df)

    print()
    print("impedance table")
    
    peak, fft=didgmo_bridge(geo)
    print(peak.get_impedance_table())
    print("-"*20)

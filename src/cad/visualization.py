class DidgeVisualizer:
    
    @classmethod
    def create_didge_shape(cls, geo):
        max_y=max([x[1] for x in geo.geo])

        df={"x":[], "y": [], "series": []}
        for i in range(0, len(geo.geo)):
            p=geo.geo[i]

            p_oben=p[1] + d1/2
            p_unten=-1*p[1] - d1/2

            df["x"].append(p[0])
            df["y"].append(p_oben)
            df["series"].append("oben")
            df["x"].append(p[0])
            df["y"].append(p_unten)
            df["series"].append("unten")
            df["x"].append(p[0])
            df["y"].append(p_unten)
            df["series"].append("seg" + str(i))
            df["x"].append(p[0])
            df["y"].append(p_oben)
            df["series"].append("seg" + str(i))

        return pd.DataFrame(df)
    
    @classmethod
    def vis_didge(cls, geo):
        df=Visualizer.create_didge_shape(geo)
        n_series=len(df["series"].unique())
        palette = ["#000000"]*n_series
        sns.set(rc={'figure.figsize':(15,3)})
        g = sns.lineplot(data=df, x="x", y="y", hue="series", palette=palette)
        #g.set(ylim=(0, y_dim))
        #g.set(xlim=(0, x_dim))
        g.get_legend().remove()
        #g.set_yticks([])
        g.xaxis.set_ticks_position("top")
        #g.show()
        plt.axis('equal')
        plt.show()
        
class FFTVisualiser:
    
    @classmethod
    def vis_fft_and_target(cls, fft, target):
        
        fft=fft.copy()
        
        fft=fft.drop(columns=["ground", "overblow", "freq"])
        for column in fft.columns:
            fft[column]=fft[column] / fft[column].max()
        sns.set(rc={'figure.figsize':(15,5)})
        sns.lineplot(data=fft)
        
        for t in target:
            note_number=Note.freq_to_note(t)
            print(t, note_number)
            plt.axvline(t, 0, 1, color="black", dashes=[5,5])
        plt.show()

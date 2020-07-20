import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import scipy.fftpack
from scipy import signal
from plotly.subplots import make_subplots
import random
import os


class PlotAcc:

    def __init__(self,
                 samp=0.005,
                 t=200,
                 jerk_perc=70,
                 manual_start=0,
                 path='C:/',
                 pre_tr=0,
                 ax_princ='Az_1',
                 wind=0):

        self.ax_princ = ax_princ            # Post-processing trigger axis
        self.samp = samp                    # 0.005 # Sampleperiod: samp=1/samplerate
        self.t = t                          # 200   # Number of samples taken during the acquisition process
        self.jerk_perc = jerk_perc          # 70    # Percentage of the jerk value to take as threshold
        self.manual_start = manual_start    # 0     # Manually starts the post processing from a certain iteration
        self.pre_tr = pre_tr                # 20    # Defines the number of samples to take into consideration before the trigger iteration
        self.wind = wind                    # 0     # acrivates the exp window function when set to 1
        self.path = path                    # path of the .csv file

    # Function that finds the .csv file into path:

    def extract_csv(self):

        dataf = ""

        for nomefile in os.listdir(self.path):
            if nomefile.startswith('Acceleration'):
                address = self.path + nomefile
                dataf = pd.read_csv(address, sep=';')
                return dataf

        if dataf == "":
            print("\n Error! .csv not found in path. \n")
            return False

    # Function that finds the trigger iteration:

    def triggcalc(self):
    
        ax_acc = self.ax_princ

        df = self.extract_csv()

        asse = df[ax_acc]
        u = asse.shape[0]
        e = 0

        deriv_acc = np.gradient(asse, self.samp)

        if self.manual_start == 0:
            jerk_cr = (self.jerk_perc/100)*np.abs(np.amax(deriv_acc))

            while True:
                if e > u-(self.t+1):
                    print('\n Error: no transient was found! \n')
                    return False
                elif deriv_acc[e] >= jerk_cr:
                    trigger = e
                    break
                else:
                    e += 1
            return {'trigger': trigger, 'deriv_acc': deriv_acc, 'jerk_cr': jerk_cr}

        else:
            trigger = self.manual_start
            jerk_cr = deriv_acc[trigger]
            return {'trigger': trigger, 'deriv_acc': deriv_acc, 'jerk_cr': jerk_cr}

    # Jerk plot as funcion of time:

    def plot_jerk(self, asse):

        pio.templates.default = "none"

        df = self.extract_csv()

        acc = df[asse]
        time = np.size(acc)
        jerk_tot = np.gradient(acc, self.samp)

        fig_j = make_subplots(specs=[[{"secondary_y": True}]])

        fig_j.add_trace(
            go.Scatter(
                name="Acceleration",
                x=np.arange(0, time, self.samp),
                y=acc,
                customdata=np.arange(0, time, 1),
                line=dict(color='red'),
                opacity=0.8,
                hovertemplate="Time: %{x:.3f} s<br>" + "Sample: %{customdata:.1f} <br>" + "Acceleration: %{y:.2f} m/s^2" + " <extra></extra>",
            ),
            secondary_y=False
        )

        fig_j.add_trace(
            go.Scatter(
                name="Jerk",
                x=np.arange(0, time, self.samp),
                y=jerk_tot,
                customdata=np.arange(0, time, 1),
                line=dict(color='blue'),
                opacity=0.8,
                hovertemplate="Time: %{x:.3f} s<br>" + "Sample: %{customdata:.1f} <br>" + "Jerk: %{y:.2f} m/s^3" + " <extra></extra>",
            ),
            secondary_y=True,
        )

        fig_j.update_layout(
            title_text="Jerk of the " + asse " axis (time domain)",
        )

        fig_j.update_xaxes(title_text="Time [s]")

        fig_j.update_layout(
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            )
        )

        fig_j.update_yaxes(title_text="Acceleration [m/s^2]", secondary_y=False, range=[-20, 20])
        fig_j.update_yaxes(title_text="jerk [m/s^3]", secondary_y=True, range=[-1.1 * np.abs(np.max(jerk_tot)), 1.1 * np.abs(np.max(jerk_tot))])

        fig_j.show()
        
        pio.write_html(fig_j, file=self.path + 'jerk ' + asse + 'axis.html', auto_open=False)

    # Windowing and plot function:

    def plot(self, asse):

        triggcalc_data = self.triggcalc()
        df = self.extract_csv()
        trigger = triggcalc_data['trigger']
        deriv_acc = triggcalc_data['deriv_acc']
        jerk_cr = triggcalc_data['jerk_cr']
        time = np.size(deriv_acc)

        pio.templates.default = "none"

        if asse == self.ax_princ:
            if self.manual_start == 0:
                print(" \n Critic Jerk: ", round(jerk_cr), "m/s^3 \n")
                tab1 = go.Figure(
                    data=go.Table(
                        header=dict(values=["Principal axis", "Jerk Trigger Threshold[m/s^3]",
                                            'Trigger iteration of the principal axis', "Jerk Trigger Value [m/s^3]"]),
                        cells=dict(values=[self.ax_princ, round(jerk_cr), trigger, round(deriv_acc[trigger])]),
                        visible=True),
                    layout=go.Layout(
                        title='Trigger result:'
                    )
                )
            else:
                tab1 = go.Figure(
                    data=go.Table(
                        header=dict(values=["Principal axis", 'Manual start iteration', "Start Jerk [m/s^3]"]),
                        cells=dict(values=[self.ax_princ, trigger, round(deriv_acc[trigger])]),
                        visible=True),
                    layout=go.Layout(
                        title='Manual iteration:'
                    )
                )

            jerk_tot = go.Scatter(
                x=np.arange(0, time, self.samp),
                y=deriv_acc,
                customdata=np.arange(0, time, 1),
                line=dict(color='blue'),
                opacity=0.8,
                hovertemplate="Time: %{x:.3f} s <br>" + "Sample: %{customdata:.1f} <br>" + "Jerk: %{y:.2f} m/s^3 <br>" + " <extra></extra>",
            )

            fig1 = go.Figure(data=jerk_tot)

            fig1.update_layout(
                title="Principal axis jerk (time domain " + self.ax_princ + ")",
                xaxis_title="Time [s]",
                yaxis_title="Jerk [m/s^3]",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )

            pio.write_html(fig1, file=self.path + 'principal axis jerk.html', auto_open=False)
            pio.write_html(tab1, file=self.path + 'trigger tab.html', auto_open=False)


            fig1.show()
            tab1.show()

        rcolor = "#%06x" % random.randint(0, 0xFFFFFF)
        color2 = '#EB7122'
        color3 = '#7F7F7F'


        # Calculation of plot variables:

        ris = 1 / (self.t * self.samp)      # Spectral resolution
        f_max = int((1 / self.samp) / 2)    # Maximum sampling frequency as stated in Nyquist-Shannon Th
        s = self.t // 2                     # Floor division of the number of samples

        acc = df[asse]

        # Check window option:

        if self.wind:
            window = signal.windows.exponential(M=self.t, center=0, tau=self.t/5, sym=False)
            acc_fin = window * acc[trigger - self.pre_tr:trigger + self.t - self.pre_tr]
        else:
            acc_fin = acc[trigger - self.pre_tr:trigger + self.t - self.pre_tr]

        jerk_arr = np.gradient(acc_fin, self.samp)

        # Data post-processing

        rms = round(np.sqrt(np.mean(acc_fin ** 2)), 3)  # Root Mean Square

        peak_max = round(np.max(acc_fin), 2)
        peak_min = round(np.min(acc_fin), 2)
        peaks = [peak_max, np.abs(peak_min)]
        peak_plus = round(np.max(peaks), 2)
        peak_peak = round(peak_max - peak_min, 2)

        tab2 = go.Figure(
            data=go.Table(
                header=dict(values=["Axis", "RMS [m/s^2]", "Maximum Peak (absolute value) [m/s^2]", "Peak to Peak [m/s^2]",
                                    'Spectral resolution [Hz]']),
                cells=dict(values=[asse, rms, peak_plus, peak_peak, round(ris, 2)]),
                visible=True, ),
            layout=go.Layout(
                title='Values:'
            )
        )

        tab2.show()

        pio.write_html(tab2, file=self.path + 'acceleration tab ' + asse + '.html', auto_open=False)

        fig = make_subplots(rows=3, cols=1,
                            subplot_titles=("Time domain " + asse, "Frequency domain " + asse, "Jerk " + asse),
                            )

        freq = go.Scatter(
            x=np.arange(0, self.t * self.samp, self.samp),
            y=acc_fin,
            name="Acc. " + asse,
            line=dict(color=rcolor),
            opacity=0.8,
            hovertemplate="Time: %{x:.3f} s<br>" + "Acc: %{y:.2f} m/s^2" + " <extra></extra>",
        )

        # Fourier Transform:

        xf = np.arange(ris, f_max, ris)

        fft = 2 / self.t * np.abs(scipy.fftpack.fft(acc_fin)[1:s])
        yf = fft

        trasf = go.Scatter(
            x=xf,
            y=yf,
            name="FFT " + asse,
            mode='markers',
            marker=dict(color=color2),
            opacity=0.8,
            hovertemplate="Freq: %{x:.2f} Hz<br>" + "Amp: %{y:.2f} m/s^2" + " <extra></extra>",
        )

        fig.add_bar(x=xf, y=yf, showlegend=False, row=2, col=1, hoverinfo='skip',
                    marker=dict(
                        color=color2,
                        opacity=0.5)
                    )

        jerk = go.Scatter(
            x=np.arange(0, self.t * self.samp, self.samp),
            y=jerk_arr,
            name="Jerk " + asse,
            line=dict(color=color3),
            opacity=0.8,
            hovertemplate="Time: %{x:.3f} s<br>" + "Jerk: %{y:.2f} m/s^3" + " <extra></extra>",
        )

        fig.append_trace(freq, 1, 1)
        fig.append_trace(trasf, 2, 1)
        fig.append_trace(jerk, 3, 1)

        # Time domain layout update:

        fig.update_xaxes(row=1, col=1, showgrid=False, gridwidth=1, gridcolor='black', zerolinecolor='black', zerolinewidth=0.1, zeroline=False,
                         title_text="Time [s]", ticks="outside", tickwidth=1, tickcolor='black', ticklen=5, mirror=True, showline=True
                         )

        fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='black', zerolinecolor='black', zeroline=True,
                         title_text="Acceleration [m/s^2]", ticks="outside", tickwidth=1, tickcolor='black',
                         row=1, col=1, ticklen=5, zerolinewidth=0.1, mirror=True, showline=True
                         )

        # Frequency domain layout update:

        fig.update_xaxes(showgrid=False, gridwidth=1, gridcolor='black', zerolinecolor='black', zeroline=False, row=2, col=1,
                         mirror=True, ticks='outside', showline=True, zerolinewidth=0.1,
                         title_text="Frequency [Hz]", tickwidth=1, tickcolor='black', ticklen=5,
                         range=[-1, f_max]
                         )

        fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='black', zerolinecolor='black', zeroline=True, row=2, col=1,
                         mirror=True, ticks='outside', showline=True, zerolinewidth=0.1,
                         title_text="Amplitude [m/s^2]", tickwidth=1, tickcolor='black', ticklen=5,
                         range=[0, np.max(yf + yf / 10)]
                         )

        # Jerk plot layout update:

        fig.update_xaxes(showgrid=False, gridwidth=1, gridcolor='black', zerolinecolor='black', zeroline=False, row=3, col=1,
                         mirror=True, ticks='outside', showline=True, zerolinewidth=0.1,
                         title_text="Time [s]", tickwidth=1, tickcolor='black', ticklen=5
                         )

        fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='black', zerolinecolor='black', zeroline=True, row=3, col=1,
                         mirror=True, ticks='outside', showline=True, zerolinewidth=0.1,
                         title_text="Jerk [m/s^3]", tickwidth=1, tickcolor='black', ticklen=5
                         )

        # General layout update

        fig.update_layout(height=1020, width=1480,
                          bargap=0.75, barmode='overlay',
                          legend_orientation="h",
                          )

        # Save plots:

        pio.write_html(fig, file=self.path + 'acceleration plot ' + asse + '.html', auto_open=False)
        
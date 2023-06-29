import os
import pandas as pd
import numpy as np

from scipy import signal
from numpy.fft import fft, ifft
from openpyxl import load_workbook
from dotenv import load_dotenv

from get_emg_processing import EmgProcessing
from get_sensor_processing import AuxProcessing

load_dotenv()

class FeatureExtract:
    def __init__(self, sample_rate=2000, Arquivo="C:\\Users\\joaov\\OneDrive - Universidade Federal de Uberlândia\\IC_BioLab\\Artigo_Neuroday_2023\\Scripts em Python para EMG\\C6_PINCA.csv", sep=",", caminho="C:\\Users\\joaov\\OneDrive - Universidade Federal de Uberlândia\\IC_BioLab\\Artigo_Neuroday_2023\\Scripts em Python para EMG", colect="C6_PINCA_Features.csv"):
        self.sample_rate = sample_rate  # taxa de amostragem em Hz
        # tamanho da janela em amostras (40 ms)
        self.window_size = int(0.02 * sample_rate)
        # buffer circular de armazenamento de amostras
        self.buffer = np.zeros(self.window_size)
        self.index = 0  # índice do buffer para inserção da próxima amostra

        self.df = pd.read_csv(Arquivo)
        self.CSVFeatures = colect+"_Mean"  # Planilha para salvar os dados
        self.CSVFeatures_RMS = colect+"RMS"  # Planilha para salvar os dados

    def mean(self):
        media = pd.DataFrame(np.zeros_like(self.df), columns=self.df.columns)

        for i in self.df.columns:
            # Calcular a média em cada ponto do sinal
            media[i] = self.df[i].rolling(
                window=self.window_size, center=True).mean()
            media[i].iloc[:self.window_size //
                          2] = media[i].iloc[self.window_size//2]
            media[i].iloc[-self.window_size //
                          2:] = media[i].iloc[-self.window_size//2-1]

        if os.path.isfile(self.CSVFeatures):
            Savecvs = pd.read_csv(self.CSVFeatures)
            Savecvs = pd.concat(
                [Savecvs, media.add_prefix("Mean_")], axis=1)
            media.to_csv(self.CSVFeatures, index=False)

        else:
            media.add_prefix("Mean_").to_csv(
                self.CSVFeatures, mode='a', index=False)

    def RMS(self):
        rms = pd.DataFrame(np.zeros_like(self.df), columns=self.df.columns)
        for i in self.df.columns:
            values = self.df[i].values
            squared_values = np.square(values)
            windowed_squared_values = squared_values.reshape(
                -1, self.window_size)
            mean_squared_values = np.mean(windowed_squared_values, axis=1)
            rms_values = np.sqrt(mean_squared_values)
            rms[i].append(rms_values)

        if os.path.isfile(self.CSVFeatures_RMS):
            Savecvs = pd.read_csv(self.CSVFeatures_RMS)
            Savecvs = pd.concat(
                [Savecvs, rms.add_prefix("RMS_  ")], axis=1)
            rms.to_csv(self.CSVFeatures_RMS, index=False)

        else:
            rms.add_prefix("RMS_").to_csv(
                self.CSVFeatures_RMS, mode='a', index=False)
    # def FeatureExtract(self):

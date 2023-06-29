import os
import pandas as pd
import numpy as np

from scipy import signal
from dotenv import load_dotenv

load_dotenv()


class AuxProcessing:
    def __init__(self, fs=2000, Arquivo="C:\\Users\\joaov\\OneDrive - Universidade Federal de Uberlândia\\IC_BioLab\\Artigo_Neuroday_2023\\Scripts em Python para EMG\\C6_PincaCc.csv", sep=",", caminho="C:\\Users\\joaov\\OneDrive - Universidade Federal de Uberlândia\\IC_BioLab\\Artigo_Neuroday_2023\\Scripts em Python para EMG", colect="C6_PINCA.csv"):

        self.csv_Sensor = colect  # Planilha para salvar os dados

        self.Aux_RawData = pd.read_csv(Arquivo)

        if len(self.Aux_RawData.columns) == 7:
            self.Aux_RawData.columns = ["C2", "C3",
                                        "C4", "AUX1", "AUX2", "AUX3", "AUX4"]
            self.Aux_RawData = self.Aux_RawData.loc[:, [
                "AUX1", "AUX2", "AUX3", "AUX4"]]
        else:
            self.Aux_RawData.columns = [
                "C2", "C3", "C4", "AUX1", "AUX2", "AUX3"]
            self.Aux_RawData = self.Aux_RawData.loc[:, [
                "AUX1", "AUX2", "AUX3"]]

        self.Zeros_FullMatrix = np.zeros(
            (self.Aux_RawData.shape[0], self.Aux_RawData.shape[1]))

        self.Aux_FillData = pd.DataFrame(self.Zeros_FullMatrix)
        self.Aux_FillData.columns = self.Aux_RawData.columns


        self.Zeros_WinMatrix = np.zeros((4600, 5))
        self.EMG_FillWin = pd.DataFrame(self.Zeros_WinMatrix)
        self.EMG_FillWin.columns = [
            "Cont1", "Cont2", "Cont3", "Cont4", "Cont5"]

        # Inicio de cada janela = [4.0, 8.0, 12.0, 16.0, 20.0]
        self.Init_Win = np.arange(int(os.environ.get('START')), len(
            self.Aux_RawData['AUX1'])-int(os.environ.get('WIN_SIZE')), int(os.environ.get('START')))

    def filter(self, FilterAuxsignal):

        for i in FilterAuxsignal.columns:
            b, a = signal.butter(int(os.environ.get('AUX_ORDER')), float(
                os.environ.get('AUX_LOW')), 'low', analog=False)
            FilterAuxsignal[i] = signal.filtfilt(
                b, a, FilterAuxsignal[i], axis=0)

        return FilterAuxsignal

    def SignalWind(self, FiltredSignal):
        self.FiltredSignal = FiltredSignal
        # iniciando um vetor com zeros -> Armazenar sinal janelado com tempo de 25 segundos
        windowSigT = self.Aux_FillData
        # iniciando um vetor com zeros -> Armazenar sinal janelado final com tempo de 23segundos
        WindowSig = self.EMG_FillWin
        Savecvs = self.EMG_FillWin

        for z in self.Aux_FillData .columns:  # Pegando o nome das colunas do df ForWindF

            # Criando as janelas de sinal
            for i in range(len(windowSigT['AUX1'])):
                for j in range(1, len(self.Init_Win)+1):
                    if (i >= (int(os.environ.get('START'))*j)-500) and (i <= int(os.environ.get('STEP'))+(int(os.environ.get('START'))*j)+100):
                        windowSigT[z][i] = 1
                        windowSigT[z][i] = self.FiltredSignal[z][i] * \
                            windowSigT[z][i]

            w = 1
            # Laço que ira percorrer os nomes do df Windf = {cont1, cont2, cont3, cont4, cont5}
            for j in self.EMG_FillWin.columns:
                WindowSig[j][0:len(WindowSig)] = windowSigT[z][(
                    int(os.environ.get('START'))*w)-500:int(os.environ.get('STEP'))+(int(os.environ.get('START'))*w)+100]
                w += 1

            # iniciando um vetor com zeros -> Armazenar sinal janelado final com tempo de 23segundos
            WindowSig = self.EMG_FillWin

            if os.path.isfile(self.csv_Sensor):
                Savecvs = pd.read_csv(self.csv_Sensor)
                Savecvs = pd.concat(
                    [Savecvs, WindowSig.add_prefix(z+"_")], axis=1)
                Savecvs.to_csv(self.csv_Sensor, index=False)

            else:
                WindowSig.add_prefix(
                    z+"_").to_csv(self.csv_Sensor, mode='a', index=False)

    def ProcessedAux(self):

        instance = AuxProcessing()
        FiltredAux = instance.filter(self.Aux_RawData)
        instance.SignalWind(FiltredAux)

import os
import pandas as pd
import numpy as np

from scipy import signal
from numpy.fft import fft, ifft
from openpyxl import load_workbook
from dotenv import load_dotenv

load_dotenv()


class EmgProcessing:

    def __init__(self, File='C6_PincaCc.csv', colect="C6_PINCA.csv"):

        self.colect = colect
        self.csv_EMG = colect

        self.EMG_RawData = pd.read_csv(
            'C:\\Users\\joaov\\OneDrive - Universidade Federal de Uberlândia\\IC_BioLab\\Artigo_Neuroday_2023\\Scripts em Python para EMG\\EMG_RawData\\'+File)

        if len(self.EMG_RawData.columns) == 7:
            self.EMG_RawData.columns = ["C2", "C3",
                                        "C4", "AUX1", "AUX2", "AUX3", "AUX4"]
            self.EMG_RawData = self.EMG_RawData.loc[:, ["C2", "C3", "C4"]]

        else:
            self.EMG_RawData.columns = [
                "C2", "C3", "C4", "AUX1", "AUX2", "AUX3"]
            self.Aux_RawData = self.EMG_RawData.loc[:, ["C2", "C3", "C4"]]

        # Criando um dataframe para salvar dados necessários nos metodos
        self.Zeros_FullMatrix = np.zeros(
            (self.EMG_RawData.shape[0], self.EMG_RawData.shape[1]))
        self.EMG_FillData = pd.DataFrame(self.Zeros_FullMatrix)
        self.EMG_FillData.columns = self.EMG_RawData.columns

        self.Zeros_WinMatrix = np.zeros((4600, 5))
        self.EMG_FillWin = pd.DataFrame(self.Zeros_WinMatrix)
        self.EMG_FillWin.columns = [
            "Cont1", "Cont2", "Cont3", "Cont4", "Cont5"]

        # Inicio de cada janela = [4.0, 8.0, 12.0, 16.0, 20.0]
        self.Init_Win = np.arange(int(os.environ.get('START')), len(
            self.EMG_RawData.iloc[:, 1])-int(os.environ.get('WIN_SIZE')), int(os.environ.get('START')))

    def EmgFilter(self):

        nyqs = 0.5*int(os.environ.get('FS'))
        low = int(os.environ.get("EMG_LOWCUT"))/nyqs
        high = int(os.environ.get("EMG_HIGHCUT"))/nyqs
        b, a = signal.butter(int(os.environ.get("EMG_FIL_ORDER")), [
                             low, high], 'bandpass', analog=False)

        # Criando um dataframe para salvar os dados filtrados do sinal com n linhas e m colunas
        self.EMG_FiltSignal = self.EMG_FillData

        # Realizando a filtragem do sinal de 20 a 500Hz
        for i in self.EMG_FiltSignal.columns:
            self.EMG_FiltSignal[i] = signal.filtfilt(
                b, a, self.EMG_RawData[i], axis=0)

        return self.EMG_FiltSignal

    def NotFilter60Hz(self, EMG_Signal):

        # Criando um df para aplicar o filtro de dados
        EMG_NOTFiltSignal = self.EMG_FillData

        for i in EMG_NOTFiltSignal.columns:
            b_notch, a_notch = signal.iirnotch((int(os.environ.get(
                'NOTCH_FREQ'))*5)-5, int(os.environ.get('QUAL_FACTOR')), int(os.environ.get('FS')))
            EMG_NOTFiltSignal[i] = signal.filtfilt(
                b_notch, a_notch, EMG_Signal[i])

            j = np.arange(1, 8, 1)
            for number in j:
                b_notch, a_notch = signal.iirnotch(int(os.environ.get(
                    'NOTCH_FREQ'))*number, int(os.environ.get('QUAL_FACTOR')), int(os.environ.get('FS')))
                EMG_NOTFiltSignal[i] = signal.filtfilt(
                    b_notch, a_notch, EMG_NOTFiltSignal[i])

        return EMG_NOTFiltSignal

    def FindOutliers(self, EMG_Signal):

        for i in EMG_Signal.columns:
            EMG_Signal[['mean', 'std']] = EMG_Signal[i].rolling(
                window=400).agg(['mean', 'std']).fillna(0)

            for y in range(len(EMG_Signal)):
                if ((EMG_Signal[i][y] < -2.5*EMG_Signal['std'][y]) and (EMG_Signal[i][y] < 0)):
                    EMG_Signal[i][y] = -2.5*EMG_Signal['std'][y]
                elif ((EMG_Signal[i][y] > 2.5*EMG_Signal['std'][y]) and (EMG_Signal[i][y] > 0)):
                    EMG_Signal[i][y] = 2.5*EMG_Signal['std'][y]

        return EMG_Signal.drop(['mean', 'std'], axis=1)

    def SignalWind(self, FiltredSignal):

        EMG_FullWin = self.EMG_FillData  # EMG_FullWin
        EMG_ContWin = self.EMG_FillWin  # EMG_ContWin
        Savecvs = self.EMG_FillWin

        for z in self.EMG_FillData.columns:  # Pegando o nome das colunas do df ForWindF
            # Criando as janelas de sinal
            for i in range(len(EMG_FullWin['C2'])):
                for j in range(1, len(self.Init_Win)+1):
                    if (i >= (int(os.environ.get('START'))*j)-500) and (i <= (int(os.environ.get('STEP')))+(int(os.environ.get('START'))*j)+100):
                        EMG_FullWin[z][i] = 1
                        EMG_FullWin[z][i] = FiltredSignal[z][i] * \
                            EMG_FullWin[z][i]

            w = 1
            # Laço que ira percorrer os nomes do df Windf = {cont1, cont2, cont3, cont4, cont5}
            for j in self.EMG_FillWin.columns:
                EMG_ContWin[j][0:len(EMG_ContWin)] = EMG_FullWin[z][(
                    int(os.environ.get('START'))*w)-500:int(os.environ.get('STEP'))+(int(os.environ.get('START'))*w)+100]
                w += 1

            # iniciando um vetor com zeros -> Armazenar sinal janelado final com tempo de 23segundos
            EMG_ContWin = self.EMG_FillWin

            if os.path.isfile(self.csv_EMG):
                Savecvs = pd.read_csv(self.csv_EMG)
                Savecvs = pd.concat(
                    [Savecvs, EMG_ContWin.add_prefix(z+"_")], axis=1)
                Savecvs.to_csv(self.csv_EMG, index=False)

            else:
                EMG_ContWin.add_prefix(
                    z+"_").to_csv(self.csv_EMG, mode='a', index=False)

    def ProcessedEMG(self):
        # Instanciando a classe EmgProcessing permitindo chamar outro metodo
        '''
        instance = EmgProcessing()
        EMG_FiltSig = instance.EmgFilter()
        EMG_NotFiltSig = instance.NotFilter60Hz(EMG_FiltSig)
        EMG_FindOutSig = instance.FindOutliers(EMG_NotFiltSig)
        instance.SignalWind(EMG_FindOutSig)
        '''
        print(type(os.environ.get('DIR_RAW')))
        print(type(self.colect))

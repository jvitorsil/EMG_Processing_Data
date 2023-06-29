from get_emg_processing import EmgProcessing
from get_sensor_processing import AuxProcessing
from get_feature import FeatureExtract


if __name__ == "__main__":

    EMG = EmgProcessing()
    EMG.ProcessedEMG()

    # aux = AuxProcessing()
    # aux.ProcessedAux()

    # feat = FeatureExtract()
    # feat.mean()

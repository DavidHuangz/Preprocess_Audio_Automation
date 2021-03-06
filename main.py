import concurrent.futures
import os.path
import time

# Other files
from Processes.AudioEnchance import enhance_audio
from Processes.WebMAUS import WebMAUS_process
from Processes.G2P import G2P_process
from Processes.personalPepeha import personalPepeha
from Processes.makeTextFile import makeTextFile

from HelperFunctions import *
from Constants import Num_threads


def main():
    t1 = time.perf_counter()

    # Empty all relevant folders used for processing
    emptyFolder(AudioEnhanceOutput)
    time.sleep(0.5)  # Extra delay for deleting
    emptyFolder(TextFile)
    time.sleep(0.5)  # Extra delay for deleting
    emptyFolder(G2POutputFiles)
    time.sleep(0.5)  # Extra delay for deleting
    emptyFolder(WebMAUSOutputFile)

    # step 1 - Convert all audio files to wav type concurrently in
    # Constants.py

    # step 2 - Remove all personal Pepeha audio files
    personalPepeha()

    makeTextFile()  # step 3 - Make all text files for G2P - .Par files

    # Concurrent datachunks processing for each thread
    dataChunks = []
    for x in range(Num_threads):
        dataChunks.append(x)

    dataChunkProcess(AudioFiles, '')  # step 3 - Separate audio into chunks for each thread
    # Enhance audio process
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(enhance_audio, dataChunks)  # step 4 - processing raw audio to enhance audio

    dataChunkProcess(TextFile, '')  # step 5 - Separate text files into chunks for each thread
    # Enhance G2P process
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(G2P_process, dataChunks)  # step 6 - processing enhance audio to .par files

    dataChunkProcess(AudioEnhanceOutput, G2POutputFiles)  # step 7 - Two separate chunks for two uploads for WebMAUS
    # Enhance WebMAUS process for generating text grids
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(WebMAUS_process, dataChunks)  # step 8 - processing text grids from .par and enhanced audio files

    t2 = time.perf_counter()

    print(f'Finished in {round(t2 - t1, 2)} second(s)' + ' with ' + str(Num_threads) + ' thread(s)')
    processedFiles = os.listdir(WebMAUSOutputFile)
    print('Processed ' + str(len(processedFiles)) + ' files')


if __name__ == '__main__':
    main()

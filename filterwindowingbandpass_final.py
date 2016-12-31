from pylab import *
import numpy as np
import wave
import sys
import math
import contextlib
from scipy.signal import *

fname = 'input.wav'
outname = 'filtered.wav'

#Credits to Matti Pastell for the plotting functions
#They can be found here http://mpastell.com/2010/01/18/fir-with-scipy/

#Freq and phase response plotting function
def impz(b,a=1):

    l = len(b)
    impulse = repeat(0.,l); impulse[0] =1.
    x = arange(0,l)
    response = lfilter(b,a,impulse)
    subplot(211)
    stem(x, response)
    ylabel('Amplitude')
    xlabel(r'n (samples)')
    title(r'Impulse response')
    subplot(212)
    step = cumsum(response)
    stem(x, step)
    ylabel('Amplitude')
    xlabel(r'n (samples)')
    title(r'Step response')
    subplots_adjust(hspace=0.5)

#Step and impulse response plotting function    
def mfreqz(b,a=1):
    w,h = freqz(b,a)
    h_dB = 20 * log10 (abs(h))
    subplot(211)
    plot(w/max(w),h_dB)
    ylim(-150, 5)
    ylabel('Magnitude (db)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Frequency response')
    subplot(212)
    h_Phase = unwrap(arctan2(imag(h),real(h)))
    plot(w/max(w),h_Phase)
    ylabel('Phase (radians)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Phase response')
    subplots_adjust(hspace=0.5)

def interpret_wav(raw_bytes, n_frames, n_channels, sample_width, interleaved = True):

    if sample_width == 1:
        dtype = np.uint8 # unsigned char
    elif sample_width == 2:
        dtype = np.int16 # signed 2-byte short
    else:
        raise ValueError("Hanya mendukung format audio 8 dan 16-bit")

    channels = np.fromstring(raw_bytes, dtype=dtype)

    if interleaved:
        channels.shape = (n_frames, n_channels)
        channels = channels.T
    else:
        channels.shape = (n_channels, n_frames)

    return channels 
    
    #mengambil properti-properti file input
with contextlib.closing(wave.open(fname,'rb')) as spf:
    sampleRate = spf.getframerate()
    sampWidth = spf.getsampwidth()
    nChannels = spf.getnchannels()
    nFrames = spf.getnframes()

    #fungsi utama:

    print('FIR band-pass filter windowing method untuk audio WAV')
    print('Siapkan file WAV bernama input.wav sebagai input')
    #menampilkan perintah untuk input frekuensi
    freqHi = int(input('Masukkan batas atas frekuensi (Hz): '))
    freqLow = int(input('Masukkan batas bawah frekuensi (Hz): '))
    freqHi = freqHi/((sampleRate)/2)
    freqLow = freqLow/((sampleRate)/2)
    
    
    #mengekstrak audio dari file wav
    signal = spf.readframes(nFrames*nChannels)
    spf.close()
    channels = interpret_wav(signal, nFrames, nChannels, sampWidth, True)
    
    
    #frequency yang dipakai di filter adalah normalized frequency
    a = firwin(1001, cutoff = 0.3, window = 'blackmanharris')
    bpf = firwin(1001, cutoff=[freqLow, freqHi], window='blackmanharris',pass_zero=False) 
    channels[0] = channels[0]*0.8   
    filtered = lfilter(bpf,[1], channels[0]).astype(channels.dtype)
   
    
    #Mengoutput ke file wav output
    wav_file = wave.open(outname, "w")
    wav_file.setparams((1, sampWidth, sampleRate, nFrames, spf.getcomptype(), spf.getcompname()))
    wav_file.writeframes(filtered.tobytes('C'))
    wav_file.close()
    mfreqz(bpf)
    show()
    figure(2)
    impz(bpf)
    show()

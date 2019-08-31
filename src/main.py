from network import Network
from inference import Inference
from midi_decoder import SingleTrackMidiDecoder
from midi_encoder import SingleTrackMidiEncoder
import sys
import numpy as np
import mido

if __name__ == '__main__':
    midi = SingleTrackMidiDecoder('data/scale_chords_small/midi/scale_a_mixolydian.mid', track=0, resolution=4)

    network = Network(midi, beats_in_window=4) # i.e. 1 bar
    #network.train(epochs=2)

    #network.save('a_mix.h5')

    composer = Inference()
    #composer.load_trained_from_network(network)
    composer.load_trained_from_file('a_mix.h5')

    output = composer.compose(primer=network.X, length=2, initial=0)
    #np.set_printoptions(threshold=sys.maxsize)
    #print(output.shape)
    #print(output[0:20])

    #running = True
    #while running:
        #threshold = float(input('Threshold? > '))

    song = SingleTrackMidiEncoder(output, resolution=4, ticks_per_beat=midi.tpb, 
                                    bpm=120, min_note=midi.min_note, threshold=0.1, melody_only=True)
    song.play()

    #    do_save = input('Save? [y/n] > ')
    #    if do_save == 'y':
    #        running = False
    #    elif do_save =='n':
    #        running = True

    song.save('tmp.mid')
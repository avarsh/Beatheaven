from network import Network
from midi_decoder import SingleTrackMidiDecoder
from midi_encoder import SingleTrackMidiEncoder
import sys
import numpy as np
import mido

if __name__ == '__main__':
    midi = SingleTrackMidiDecoder('data/scale_chords_small/midi/scale_c_ionian.mid', track=1, resolution=4, bpm=108)

    network = Network(midi)
    network.train(epochs=250)

    output = network.compose(1, 0)
    np.set_printoptions(threshold=sys.maxsize)
    print(output[0:20])

    #running = True
    #while running:
        #threshold = float(input('Threshold? > '))

    song = SingleTrackMidiEncoder(output, resolution=2, ticks_per_beat=midi.tpb, 
                                    bpm=108/2, min_note=midi.min_note, threshold=0.1, melody_only=True)
    song.play()

    #    do_save = input('Save? [y/n] > ')
    #    if do_save == 'y':
    #        running = False
    #    elif do_save =='n':
    #        running = True

    song.save('tmp.mid')
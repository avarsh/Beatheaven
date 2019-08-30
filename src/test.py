from network import Network
from midi_decoder import SingleTrackMidiDecoder
from midi_encoder import SingleTrackMidiEncoder
import sys
import numpy as np

if __name__ == '__main__':
    midi = SingleTrackMidiDecoder('data/scale_chords_small/midi/scale_c_ionian.mid', resolution=4)
    network = Network(midi)
    network.train()

    output = network.compose()
    np.set_printoptions(threshold=sys.maxsize)
    song = SingleTrackMidiEncoder(output[0], resolution=4, ticks_per_beat=midi.tpb, bpm=120, min_note=midi.min_note, threshold=0.1)
    print(song.roll[0:10])
import mido
import subprocess
from math import floor

class SingleTrackMidiEncoder:

    def __init__(self, roll, resolution, ticks_per_beat, bpm, min_note, threshold):
        self.roll = roll 
        self.tpb = ticks_per_beat
        self.res = resolution 

        self.file = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.file.tracks.append(self.track)

        self.track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
        self.min_note = min_note

        # Digitize the roll
        for t, notes in enumerate(self.roll):
            for n, note_val in enumerate(notes):
                if note_val < threshold:
                    self.roll[t][n] = 0
                else:
                    self.roll[t][n] = 1
            

        
        
        

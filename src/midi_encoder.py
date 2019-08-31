import mido
import subprocess
from math import floor
from os import remove

class SingleTrackMidiEncoder:

    def __init__(self, roll, resolution, ticks_per_beat, bpm, min_note, threshold):
        self.roll = roll 
        self.tpb = ticks_per_beat
        self.res = resolution 

        self.file = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.file.tracks.append(self.track)

        self.track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        self.min_note = min_note

        # Digitize the roll
        for t, notes in enumerate(self.roll):
            for n, note_val in enumerate(notes):
                if note_val < threshold:
                    self.roll[t][n] = 0
                else:
                    self.roll[t][n] = 1
            
        
        previous = [0 for t in range(len(self.roll[0]))]
        tick = 0
        last_message = 0
        for t, notes in enumerate(self.roll):
            tick = int(t * ticks_per_beat / resolution)
            for n, note_val in enumerate(notes):
                if previous[n] == 0 and note_val == 1:
                    # note on event
                    self.track.append(mido.Message('note_on', note=(n + min_note), time=(tick - last_message), channel=0, velocity=100))
                    last_message = tick
                elif previous[n] == 1 and note_val == 0:
                    self.track.append(mido.Message('note_off', note=(n + min_note), time=(tick - last_message), channel=0, velocity=100))
                    last_message = tick
        
        
    
    def save(self, filename):
        self.file.save(filename)

    def play(self):
        self.save('tmp.mid')

        cmd = ['fluidsynth', '-a', 'alsa', '-m', 'alsa_seq', '-l', '-i', \
                    '/usr/share/soundfonts/FluidR3_GM.sf2', 'tmp.mid']
        subprocess.Popen(cmd).wait()

        remove('tmp.mid')

        
        
        

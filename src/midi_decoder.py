import mido
import subprocess
from math import floor, ceil

class SingleTrackMidiDecoder:

    def __init__(self, filename, track=0, resolution=4, bpm=None):
        self.filename = filename
        self.file = mido.MidiFile(filename)
        self.track = self.file.tracks[track]
        print(self.track.name)
        self.res = resolution

        self.bpm = bpm
        self.tpb = self.file.ticks_per_beat
        self.total_ticks = 0
        for msg in self.track:
            if msg.type == 'set_tempo':
                self.bpm = mido.tempo2bpm(msg.tempo)
    
            if msg.type == 'note_on' or msg.type == 'note_off':
                self.total_ticks += msg.time
        
        # For now we only work with note_on and note_off messages
        total_notes = 127
        self.min_note = total_notes
        self.max_note = 0

        for msg in self.track:
            if msg.type == 'note_on' or msg.type == 'note_off':
                print(msg)
                if msg.note < self.min_note:
                    self.min_note = msg.note
                if msg.note > self.max_note:
                    self.max_note = msg.note

        self.note_range = (self.max_note - self.min_note) + 1
        self.roll = [[0 for j in range(self.note_range)] for i in range(self.total_ticks)]
        self.beat_roll = [[0 for j in range(self.note_range)] for i in range(ceil(self.total_ticks * self.res / self.tpb))]

        current_tick = 0
        last_tick_on = [0 for i in range(self.note_range)]

        for msg in self.track:
            if msg.type == 'note_on' and msg.velocity != 0:
                current_tick += msg.time
                last_tick_on[msg.note - self.min_note] = current_tick
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                current_tick += msg.time
                for tick in range(last_tick_on[msg.note - self.min_note], current_tick):
                    self.roll[tick][msg.note - self.min_note] = 1
                    self.beat_roll[floor(tick * self.res / self.tpb)][msg.note - self.min_note] = 1
    
    def print_messages(self):
        print("\nTrack {}".format(self.track.name))
        for msg in self.track:
            print(msg)


    def play_file(self):
        cmd = ['fluidsynth', '-a', 'alsa', '-m', 'alsa_seq', '-l', '-i', \
                    '/usr/share/soundfonts/FluidR3_GM.sf2', self.filename]
        subprocess.Popen(cmd).wait()

    
    def print_roll(self, tick_start, tick_end, note_start, note_end):
        for t in range(tick_start, tick_end):
            print("Tick {}: [...".format(t), self.roll[t][note_start:note_end], "...]")

    def print_beats(self, beat_start, beat_end):
        for b in range(beat_start, beat_end):
            print("Beat %-.3f: [..." % (b / self.res), self.beat_roll[b], "...]")


if __name__ == '__main__':
    midi = SingleTrackMidiDecoder('data/scale_chords_small/midi/scale_c_ionian.mid')
    #midi.print_messages()
    #midi.play_file()

    print("File has bpm: ", midi.bpm)
    print("Ticks per beat ", midi.tpb)
    print("Minimum note is: ", midi.min_note)
    print("Maximum note is: ", midi.max_note)
    midi.print_beats(40, 50)
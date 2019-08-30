import numpy as np
import sys
from math import floor
from keras.models import Sequential, Model
from keras.layers import LSTM, Input, Dense, RepeatVector

class Network:
    """A class representing a neural network utilising an LSTM seq2seq.

       We use an encoder-decoder model, adapted from those used for machine
       translation. An encoder takes in input in the form of a section
       of the piano roll, and outputs its internal state. The decoder
       then takes this internal state, and is trained to predict the 
       next section of music, using teacher forcing. Finally, we use the 
       trained decoder, coupled with a primer to generate music.

       By default, we use 2 bars of music.
    """

    def __init__(self, midi_in, beats_in_window=8):
        self.encoder_in_data = np.array(midi_in.beat_roll)
        self.midi_in = midi_in

        # We define the encoder inputs to be a 2d window with length defined by the
        # resolution of the midi and how many bars we want, and height as the range of
        # notes 
        '''encoder_in = Input(shape=(context_window * midi_in.res, midi_in.note_range))
        self.encoder = LSTM(20, return_state=True)
        encoder_out, h, c = encoder(encoder_in)
        # Keep the internal state of the encoder
        self.encoder_states = [h, c]

        decoder_in = Input(shape=(context_window * midi_in.res, midi_in.note_range))
        self.decoder_lstm = LSTM(20, return_sequences=True, return_state=True)
        decoder_out, _, _ = self.decoder_lstm(decoder_in, initial_state=self.encoder_states)

        decoder_dense = Dense(midi_in.note_range, activation='softmax')
        decoder_out = decoder_dense(decoder_out)

        self.model = Model([encoder_in, decoder_in], decoder_out)'''

        self.time_step = beats_in_window * midi_in.res
        total_beats = midi_in.total_ticks / midi_in.tpb
        self.N = floor((total_beats / beats_in_window)) - 1
 
        self.X = np.zeros(shape=(self.N, self.time_step, midi_in.note_range))
        self.y = np.zeros(shape=(self.N, self.time_step, midi_in.note_range))

        for i in range(0, self.N):
            beat_start = i * self.time_step
            self.X[i] = midi_in.beat_roll[beat_start:beat_start + self.time_step]
            
            if i > 0:
                self.y[i - 1] = midi_in.beat_roll[beat_start + self.time_step:beat_start + self.time_step * 2]
        
        self.hidden = 150

        # Single LSTM encoder
        self.enc_in = Input(shape=(self.time_step, midi_in.note_range))
        self.enc_lstm = LSTM(self.hidden, return_sequences=True, return_state=True)
        enc_out, enc_h, enc_c = self.enc_lstm(self.enc_in)
        self.enc_state = [enc_h, enc_c]

        # Single LSTM Decoder
        self.dec_in = Input(shape=(self.time_step, midi_in.note_range))
        self.dec_lstm = LSTM(self.hidden, return_sequences=True, return_state=True)
        dec_out, _, _ = self.dec_lstm(self.dec_in, initial_state=self.enc_state)

        self.dec_dense = Dense(midi_in.note_range, activation='softmax')
        dec_out = self.dec_dense(dec_out)

        self.model = Model(inputs=[self.enc_in, self.dec_in], outputs=[dec_out])
        

    def train(self):
        # Since we're doing multi-label classification instead of multiclass,
        # we use binary cross entropy loss
        self.model.compile(optimizer='rmsprop', loss='binary_crossentropy')
        self.model.fit([self.X, self.X], self.y, batch_size=1, epochs=50)
    
    def compose(self):
        # Create inference model
        enc = Model(self.enc_in, self.enc_state)
        
        dec_state_in = [Input(shape=(self.hidden,)), Input(shape=(self.hidden,))]

        dec_out, dec_h, dec_c = self.dec_lstm(self.dec_in, initial_state=dec_state_in)
        dec_state_out = [dec_h, dec_c]
        dec_out = self.dec_dense(dec_out)
        dec_model = Model([self.dec_in] + dec_state_in,
                          [dec_out] + dec_state_out)
        
        initial = np.random.randint(0, len(self.X) - 1)
        initial_X = self.X[initial].reshape(1, self.X.shape[1], self.X.shape[2])
        states = enc.predict(initial_X)

        target_seq = initial_X
        
        output, h, c = dec_model.predict([target_seq] + states)
        #print(output.shape)
        #print(output[0:10])

        return output



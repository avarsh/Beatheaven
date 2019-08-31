from network import Network
import numpy as np
import sys
from math import floor
from keras.models import Sequential, Model, load_model
from keras.layers import LSTM, Input, Dense, Dropout

class Inference:
    """A class which can use a trained set of encoders and decoders to generate music"""

    def __init__(self):
        self.enc_in = None
        self.enc_state = None
        self.dec_in = None
        self.dec_lstm_1 = None
        self.dec_lstm_2 = None
        self.dec_dense = None
        self.hidden = None
        
        self.enc_model = None 
        self.dec_model = None

           
    def load_trained_from_file(self, filename):
        training_model = load_model(filename)
        self.enc_in = training_model.get_layer('encoder_input').output
        enc_out, enc_h, enc_c = training_model.get_layer('encoder_lstm_output').output
        self.enc_state = [enc_h, enc_c]
    
        self.dec_in = training_model.get_layer('decoder_input')
        self.dec_lstm_1 = training_model.get_layer('decoder_lstm_input')
        self.dec_lstm_2 = training_model.get_layer('decoder_lstm_output')
        self.dec_dense = training_model.get_layer('decoder_dense')

        self._create_model()
    
    def load_trained_from_network(self, network):
        self.enc_in = network.enc_in
        self.enc_state = network.enc_state
        self.dec_in = network.dec_in
        self.dec_lstm_1 = network.dec_lstm_1
        self.dec_lstm_2 = network.dec_lstm_2
        self.dec_dense = network.dec_dense

        self._create_model()


    def _create_model(self):
        self.enc_model = Model(self.enc_in, self.enc_state)
        
        dec_state_in = [Input(shape=(self.hidden,)), Input(shape=(self.hidden,))]

        dec_out = self.dec_lstm_1(self.dec_in.output, initial_state=dec_state_in)
        dec_out, dec_h, dec_c = self.dec_lstm_2(dec_out)
        dec_state_out = [dec_h, dec_c]
        dec_out = self.dec_dense(dec_out)
        self.dec_model = Model([self.dec_in.output] + dec_state_in,
                          [dec_out] + dec_state_out)
        

    def compose(self, primer, length=1, initial=None):
        if initial == None:
            initial = np.random.randint(0, len(primer) - 1)

        initial_X = primer[initial].reshape(1, primer.shape[1], primer.shape[2])
        states = self.enc_model.predict(initial_X)

        target_seq = initial_X
        
        song = np.zeros(shape=initial_X.shape)
        song = [np.zeros(shape=initial_X.shape) for _ in range(length)]
        for i in range(length):
            output, h, c = self.dec_model.predict([target_seq] + states)
            song[i] = output[0]

            target_seq = output 
            states = [h, c]
        
        song = np.array(song)

        return song.reshape(song.shape[0] * song.shape[1], song.shape[2])
    

    def save(self, encoder_name, decoder_name):
        self.enc_model.save(encoder_name)
        self.dec_model.save(decoder_name)


    def load_inference_from_file(self, encoder_name, decoder_name):
        self.enc_model = load_model(encoder_name)
        self.dec_model = load_model(decoder_name)

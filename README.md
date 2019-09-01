# Beatheavenn

A simple neural network to generate music. Uses the ScaleChords midi dataset.

## Usage

Tested on Linux systems. Requires Keras, Tensorflow and Mido packages, as well as FluidSynth with the respective soundfonts to play the midi files.
FluidSynth can also convert the resulting midi to wav using the following command:

```fluidsynth -F output.wav -i soundfont.sf2 input.mid```
'''
Process:
    Choose one Speaker - one speaker is one channel always
    Now locate the nearest Microphone to that speaker:
        Play a sound on that speaker:
            While sound is on:
                Record a sample length in all microphones
                and store the avarage of all the mics in an array
            The maximum value of volume of mics in the list is the closest mic
            The closest mic index is the mic's device index.
            Now pair up speaker channel to microphone as tuple
        NOTE:
            One pair of speaker is one device
            So, one speaker is one of the pair (if mono)
            Combine two channels in a mic to make single mic input (avaerage channels)
            Now we have one input one outut pair.
'''


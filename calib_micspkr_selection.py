'''
Combined Calibration and Mic-Speaker Selction Process:
'''

'''
Process:
    Choose one Speaker - one speaker is one channel always
    For every speaker:
    Now locate the nearest Microphone to that speaker:
        with a start volume of 60% sysvol
        Play a Pink noise sample in the speaker:
            While sound is on:
                Record a sample length in all microphones - 5 sec @ 48khz
                and store the avarage of all the mics in an array
                The maximum value of volume of mics in the list is the closest mic
                The closest mic index is the mic's device index.
                for the next 10 sec @ 48khz:
                    for the closest mic
                    with a start volume of 30% sysvol to 70%
                    get mic reading levels with random step size change in sysvol
                    save the relevant mic inputs as x and sysvol as y as an x,y pair
                    
            Now pair up speaker channel to microphone as tuple

        Obtain the regression line equation for best fit line:
            using sklearn? kernel ridge regression
            tune hyperparameters using gridsearchCV
        
        return the regression line equation for every model(?)
        
        NOTE:
            One pair of speaker is one device
            So, one speaker is one of the pair (if mono)
            Combine two channels in a mic to make single mic input (average channels)
            Now we have one input one outut pair.

'''
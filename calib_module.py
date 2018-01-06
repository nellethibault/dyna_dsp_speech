'''
Calibration process:
    
    For every speaker:
        
        Play a Pink noise sample in the speaker
        with a start volume of 30% sysvol to 70%
        get mic reading levels with random step size change in sysvol
        save the relevant mic inputs as x and sysvol as y as an x,y pair
        
        Obtain the regression line equation for best fit line:
            using sklearn? kernel ridge regression
            tune hyperparameters using gridsearchCV
    
    return the regression line equation for every model(?)
'''
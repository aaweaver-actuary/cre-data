# this is the folder that is searched for deal sheets
folder = r'O:\PARM\Corporate Actuarial\Reserving\Assumed Reinsurance'
# folder = 'M:/Clients'

# this is the number of deal sheets to show each refresh
# (keeps the screen from getting too cluttered)
show_every=5

def get_folder():
    """
    # Description:
        Returns the folder to search for deal sheets
    # Inputs:
        None
    # Outputs:
        folder: the folder to search for deal sheets
                the folder is given above in the user_inputs.py file
    # Example:
        >>> folder = get_folder()
        >>> # expect that this will be the folder above (O:\PARM\Corporate Actuarial\Reserving\Assumed Reinsurance)
        >>> print(folder)
        O:\PARM\Corporate Actuarial\Reserving\Assumed Reinsurance
    """
    return(folder)
    
def get_show_every():
    """
    # Description:
        Returns the number of deal sheets to show each refresh
    # Inputs:
        None
    # Outputs:
        show_every: the number of deal sheets to show each refresh
                    the number is given above in the user_inputs.py file
    # Example:
        >>> show_every = get_show_every()
        >>> # expect that this will be the number above (5)
        >>> print(show_every)
        5
    """
    return(show_every)
import os
import datetime

def update_log(error, log_folder):
    """
        Report errors that occured while running the script

        Parameter:
            error [String] - Exception message to describe the problem
    """
    if not os.path.exists('./log'):
        os.mkdir('./log')
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    log_file = os.path.join(os.getcwd(), 'log', 'error_log_' + today + '.log')

    with open(log_file, mode='a') as item:
        now = datetime.datetime.now().strftime("%H:%M")
        item.write(str(f"[{now}]:{error}\n"))

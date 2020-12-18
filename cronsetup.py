import os
import math
import crontab

def enter_interval():
    interval = ''
    print("Enter the time interval in min.")
    while not interval:
        try:
            interval = int(input("->"))
        except ValueError:
            print("Enter a number.")
    return interval

def create_cronjob(sync):
    user = os.environ['USER']
    cron = crontab.CronTab(user=user)
    job = []
    interval = enter_interval()
    for s in sync:
        command = str(f'python3 -m facebook_feed_sync {s}')
        job.append(
            cron.new(command=command).minute.every(interval))
    cron.write()
    print("Written to crontab, check with 'crontab -e'")

def main():
    print("Cronjob setup for the facebook-feed-sync:\n\n")
    print("Specify a single time interval for ALL synchronization types?")
    all_option = input("(j/N)")
    if all_option.lower() == 'j':
        create_cronjob(sync=['inventory', 'price', 'text'])
    elif not all_option or all_option.lower() == 'n':
        print("Cronjob for inventory synchronization:")
        create_cronjob(sync=['inventory'])
        print("Cronjob for price synchronization:")
        create_cronjob(sync=['price'])
        print("Cronjob for text synchronization:")
        create_cronjob(sync=['text'])

if __name__ == '__main__':
    main()

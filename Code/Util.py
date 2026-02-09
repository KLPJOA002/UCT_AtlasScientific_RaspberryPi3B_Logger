import os
# Source - https://stackoverflow.com/a/6935354
# Posted by Michael Dillon
# Retrieved 2026-02-09, License - CC BY-SA 3.0

def write_and_verify(f_n,data):
    f = file(f_n,'w')
    f.write(data)
    f.flush()
    os.fsync(f.fileno())
    f.close()
    f = file(f_n,'r')
    verified = f.read()
    f.close()
    return  verified == data and f.closed

# Source - https://stackoverflow.com/q/6840711
# Posted by Ken, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-09, License - CC BY-SA 3.0

def get_partition(dev):
    os.system('fdisk -l %s > output' % dev)
    f = file('output')
    data = f.read()
    #print data
    f.close()
    return data.split('\n')[-2].split()[0].strip()

def mount_partition(partition):
    os.system('mount %s /media/mymntpnt' % partition)


def unmount_partition():
    os.system('umount /media/mymntpnt')
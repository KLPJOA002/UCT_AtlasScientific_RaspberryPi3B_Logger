# Source - https://stackoverflow.com/q/6840711
# Posted by Ken, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-09, License - CC BY-SA 3.0

class MediaScanner():
    def __init__(self):
        self.lok = thread.allocate_lock()
        self.running = True
        self.started = False

    def register_cb(self,func):
        self.cb = func

    def start(self):
        if not self.started:
            thread.start_new_thread(self.scan_thread,())

    def scan_thread(self):
        self.quit = False
        self.started = True
        last_devices = []
        while self.running:
            devices = self.scan_media()
            if (devices != last_devices):
                self.cb(devices) #call the callback as its own thread
            last_devices = devices

            time.sleep(0.1)

        self.quit = True    

    def stop(self):
        self.running = False
        while(not self.quit):
            pass
        return True

    def is_running(self):
        return self.running


    def scan_media(self):
        with self.lok:
            partitionsFile = open("/proc/partitions")
            lines = partitionsFile.readlines()[2:]#Skips the header lines
            devices = []
            for line in lines:
                words = [x.strip() for x in line.split()]
                minorNumber = int(words[1])
                deviceName = words[3]
                if minorNumber % 16 == 0:
                    path = "/sys/class/block/" + deviceName
                    if os.path.islink(path):
                        if os.path.realpath(path).find("/usb") > 0:
                            devices.append('/dev/'+deviceName)

            partitionsFile.close()

            return devices

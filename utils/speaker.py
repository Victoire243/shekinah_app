import pyttsx3


class Speaker:
    def __init__(self):
        self.speaker = pyttsx3.init()

    def say(self, text):
        try:
            self.speaker.stop()
            self.speaker.endLoop()
        except:
            pass
        self.speaker.say(text)
        self.speaker.runAndWait()

    def stop(self):
        self.speaker.stop()

    def save_to_file(self, text, file_path):
        self.speaker.save_to_file(text, file_path)

    def runAndWait(self):
        if self.speaker.isBusy():
            self.speaker.stop()
        self.speaker.runAndWait()

import pygame


class Speaker:

    @staticmethod
    def playsound(path: str, block=True):
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        if block:
            while pygame.mixer.music.get_busy():
                continue


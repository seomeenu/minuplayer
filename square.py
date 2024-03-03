import pretty_midi
import pygame
import os
import shutil
import cv2

midi = "X:/zap/KR/KR/.mid"
midi_data = pretty_midi.PrettyMIDI(midi)

outlined = True

all_notes = []
song_length = 0

if song_length < midi_data.get_end_time():
    song_length = midi_data.get_end_time()
for instrument in midi_data.instruments:
    for note in instrument.notes:
        all_notes.append(note)

bpm = 180

pygame.init()

screen_size = 720

if os.path.exists("res"):
    shutil.rmtree("res")
os.mkdir("res")

fps = 30

screen = pygame.Surface((screen_size, screen_size))

last_hit = -1
a = 0

print(f"rendering | fps: {fps} | frames: {int(fps*song_length)}")
for frame in range(int(fps*song_length)):
    try:
        screen.fill("#000000")
        play_time = frame/fps
        for note in all_notes: 
            if note.start <= frame/fps and note.end >= frame/fps:
                if note.start != last_hit:
                    last_hit = note.start
                    a = 200
                a *= 0.8
                if outlined:
                    if int(a/2) > 0:
                        pygame.draw.rect(screen, "#ffffff", [a/2, a/2, screen_size-a, screen_size-a], int(a/2))
                else:
                    pygame.draw.rect(screen, "#ffffff", [a/2, a/2, screen_size-a, screen_size-a])

        pygame.image.save(screen, f"res/{frame}.png")
    except KeyboardInterrupt:
        break

print("making video")
video = cv2.VideoWriter(f"{midi[:-4]}.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (screen_size, screen_size))

for file in sorted(os.listdir("res"), key=len):
    image = cv2.imread(f"res/{file}")
    video.write(image)

print("video done")
cv2.destroyAllWindows()
video.release()
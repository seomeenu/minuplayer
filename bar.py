import pretty_midi
import pygame
import os
import shutil
import cv2

note_lowest = 131
note_highest = 0

song_length = 110

bpm = 180
num = 4
sec_per_beat = 60/bpm 
sec_per_bar = sec_per_beat*num

pygame.init()

screen_width = 100
screen_height = 10

if os.path.exists("res"):
    shutil.rmtree("res")
os.mkdir("res")

old_play_time = -1
fps = 30

screen = pygame.Surface((screen_width, screen_height))
print(f"rendering | fps: {fps} | frames: {int(fps*song_length)}")
for frame in range(int(fps*song_length)):
    try:
        screen.fill("#000000")
        play_time = int(frame/fps/sec_per_bar)*sec_per_bar
        pygame.draw.rect(screen, "#ffffff", [0, 0, (frame/fps-play_time)/sec_per_bar*screen_width, screen_height])

        pygame.image.save(screen, f"res/{frame}.png")
    except KeyboardInterrupt:
        break
    
print("making video")
video = cv2.VideoWriter(f"bar_{bpm}.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (screen_width, screen_height))

for file in sorted(os.listdir("res"), key=len):
    image = cv2.imread(f"res/{file}")
    video.write(image)

print("video done")
cv2.destroyAllWindows()
video.release()
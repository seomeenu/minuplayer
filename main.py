import pygame
import sys
import pretty_midi
import cv2
import os
import shutil

from easing_functions import *

pygame.init()

screen_width = 1280
screen_height = 720

clock = pygame.time.Clock()

dt = 1

# first = bottom, last = top
midis = [
    "saltchord.mid",
    "saltbass.mid",
    "saltmel.mid"
]

midi_datas = [pretty_midi.PrettyMIDI(i) for i in midis]

#pallete : https://lospec.com/palette-list/autumn-glow
colors = [
    "#ffd8a9",
    "#f2af92",
    "#f39d91",
]

layer_count = len(midis)

start_time = pygame.time.get_ticks()+1000 # <- 1000ms delay
play_time = 0

note_lowest = 131
note_highest = 0

all_notes = []
song_length = 0
for i, midi_data in enumerate(midi_datas):
    if song_length < midi_data.get_end_time():
        song_length = midi_data.get_end_time()
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            if note_lowest > note.pitch:
                note_lowest = note.pitch
            if note_highest < note.pitch:
                note_highest = note.pitch
            all_notes.append([note, i])

song_length += 2 # <- 1s

note_margin = 2

note_count = note_highest-note_lowest+note_margin

note_h = screen_height/(note_count+note_margin+1)
note_slim = 1.5
zoom = 300

bar_x = 300

ease_out = ExponentialEaseOut(1, 0, 1)
pulse_strength = 10
pulse_length = 1

if os.path.exists("res"):
    shutil.rmtree("res")
os.mkdir("res")

preview = False
if preview:
    screen = pygame.display.set_mode((screen_width, screen_height))
    while True:
        screen.fill("#533a44")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        play_time = (pygame.time.get_ticks()-start_time)/1000
        for note, i in all_notes:
            note_x = (note.start-play_time)*zoom+bar_x
            note_length = note.end-note.start
            if screen_width > note_x and note_x+note_length*zoom > 0:
                a = 0
                if note_x < bar_x:
                    a = ease_out((play_time-note.start)/pulse_length)*pulse_strength
                pygame.draw.rect(screen, colors[i], [note_x, (note_count-note.pitch+note_lowest)*note_h-a/2, note_length*zoom, note_h/note_slim+a])
                    
        pygame.draw.line(screen, "#ffffe1", [bar_x, 0], [bar_x, screen_height], 4)

        dt = clock.tick(120)*60/1000

        if play_time > song_length:
            print("end")

        pygame.display.update()
else:
    #render
    screen = pygame.Surface((screen_width, screen_height))
    fps = 30
    for frame in range(int(fps*song_length)):
        try:
            screen.fill("#533a44")
            play_time = frame/fps-1

            for note, i in all_notes:
                note_x = (note.start-play_time)*zoom+bar_x
                note_length = note.end-note.start
                if screen_width > note_x and note_x+note_length*zoom > 0:
                    a = 0
                    if note_x < bar_x:
                        a = ease_out((play_time-note.start)/pulse_length)*pulse_strength
                    pygame.draw.rect(screen, colors[i], [note_x, (note_count-note.pitch+note_lowest)*note_h-a/2, note_length*zoom, note_h/note_slim+a])
                        
            pygame.draw.line(screen, "#ffffe1", [bar_x, 0], [bar_x, screen_height], 4)

            pygame.image.save(screen, f"res/{frame}.png")
        except KeyboardInterrupt:
            break

    video = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"XVID"), 30, (screen_width, screen_height))

    for file in sorted(os.listdir("res"), key=len):
        image = cv2.imread(f"res/{file}")
        video.write(image)

    cv2.destroyAllWindows()
    video.release()
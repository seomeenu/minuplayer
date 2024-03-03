import pretty_midi
import pygame
import os
import shutil
import cv2

midi = "midis/old/kap.mid"
midi_data = pretty_midi.PrettyMIDI(midi)

note_lowest = 131
note_highest = 0

all_notes = []
song_length = 0

if song_length < midi_data.get_end_time():
    song_length = midi_data.get_end_time()
for instrument in midi_data.instruments:
    for note in instrument.notes:
        if note_lowest > note.pitch:
            note_lowest = note.pitch
        if note_highest < note.pitch:
            note_highest = note.pitch
        all_notes.append(note)

bpm = 105
num = 3
sec_per_beat = 60/bpm 
sec_per_bar = sec_per_beat*num

pygame.init()

screen_width = 1280
screen_height = 720

note_margin = 2
note_count = note_highest-note_lowest+note_margin
note_h = screen_height/(note_count+note_margin+1)
zoom = screen_width/sec_per_bar

if os.path.exists("res"):
    shutil.rmtree("res")
os.mkdir("res")
screen = pygame.Surface((screen_width, screen_height))
for frame in range(int(song_length/sec_per_bar)):
    try:
        screen.fill("#000000")
        play_time = frame*sec_per_bar
        for note in all_notes:
            note_x = (note.start-play_time)*zoom
            if screen_width >= note_x >= -1:
                note_length = (note.end-note.start)*zoom-1 #1pixel
                # if screen_width >= note_x >= 0:
                pygame.draw.rect(screen, "#ffffff", [note_x, (note_count-note.pitch+note_lowest)*note_h, note_length, note_h])

        pygame.image.save(screen, f"res/{frame}.png")
    except KeyboardInterrupt:
        break
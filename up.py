import pretty_midi
import pygame
import os
import shutil
import cv2

midi = "midis/old/arp.mid"
midi_data = pretty_midi.PrettyMIDI(midi)

note_lowest = 131
note_highest = 0

all_notes = []
song_length = 0

note_bounce = 1

if song_length < midi_data.get_end_time():
    song_length = midi_data.get_end_time()
for instrument in midi_data.instruments:
    for note in instrument.notes:
        if note_lowest > note.pitch:
            note_lowest = note.pitch
        if note_highest < note.pitch:
            note_highest = note.pitch
        all_notes.append([note, note_bounce])

bpm = 180
num = 4
sec_per_beat = 60/bpm
sec_per_bar = sec_per_beat*num

pygame.init()

screen_width = 1280
screen_height = 720

note_margin = 2+4+1
note_count = note_highest-note_lowest+note_margin
note_h = screen_height/(note_count+note_margin+1)
zoom = screen_width/sec_per_bar

if os.path.exists("res"):
    shutil.rmtree("res")
os.mkdir("res")

fps = 30

screen = pygame.Surface((screen_width, screen_height))

old_play_time = -1
a = 0
movement = 4
# ghost_notes = True

print(f"rendering | fps: {fps} | frames: {int(fps*song_length)}")
for frame in range(int(fps*song_length)):
# for frame in range(int(song_length/sec_per_bar)):
    try:
        play_time = int(frame/fps/sec_per_bar)*sec_per_bar
        if old_play_time != play_time:
            old_play_time = play_time
            a = movement
        a *= 0.8
        screen.fill("#000000")
        for note_data in all_notes:
            note = note_data[0]
            note_x = (note.start-play_time)*zoom 
            if screen_width >= note_x >= -1:
                note_length = (note.end-note.start)*zoom-1
                if note.start <= frame/fps:
                    note_data[1] *= 0.8
                    pygame.draw.rect(screen, "#ffffff", [note_x, (note_count-note.pitch+note_lowest+a+note_data[1])*note_h, note_length, note_h])
                # elif ghost_notes:
                #     pygame.draw.rect(screen, "#ffffff", [note_x, (note_count-note.pitch+note_lowest+a)*note_h, note_length, note_h], 4)

        pygame.image.save(screen, f"res/{frame}.png")
    except KeyboardInterrupt:
        break

print("making video")
video = cv2.VideoWriter(f"{midi[:-4]}.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (screen_width, screen_height))

for file in sorted(os.listdir("res"), key=len):
    image = cv2.imread(f"res/{file}")
    video.write(image)

print("video done")
cv2.destroyAllWindows()
video.release()
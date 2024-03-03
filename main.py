import pygame
import sys
import pretty_midi
import cv2
import os
import shutil
import json

pygame.init()

screen_width = 1280
screen_height = 720

clock = pygame.time.Clock()

dt = 1

#configs

# first = bottom, last = top
midis = []

bg_color = "#45444f"
bar_color = "#f2f0e5"
colors = []

start_delay = 1000
note_slim = 1.5

title = "title"
desc = "desc"

pulse_strength = 50
pulse_length = 1

preview = False

def color_overlay(color1, color2, alpha):
    bg1 = pygame.Surface((1, 1))
    bg1.fill(color1)
    bg2 = pygame.Surface((1, 1))
    bg2.fill(color2)
    bg2.set_alpha(alpha)
    bg1.blit(bg2, (0, 0))
    return bg1.get_at((0, 0))

with open("config.json") as file:
    data = json.load(file)
    midis = data["midis"]
    
    bg_color = data["bg_color"]
    bar_color = data["bar_color"]
    colors = data["colors"]
    p_colors = []
    for color in colors:
        p_colors.append(color_overlay(color, "#ffffff", 50))

    start_delay = data["start_delay"]
    note_slim = data["note_slim"]
    title = data["title"]
    desc = data["desc"]
    pulse_strength = data["pulse_strength"]
    pulse_length = data["pulse_length"]
    preview = data["preview"]
    
#configs end

midi_datas = [pretty_midi.PrettyMIDI(i) for i in midis]

layer_count = len(midis)

start_time = pygame.time.get_ticks()+start_delay # <- 1000ms delay
play_time = 0

note_lowest = 131
note_highest = 0

all_notes = {}
for i in range(layer_count):
    all_notes[i] = []
    
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
            all_notes[i].append([note, pulse_strength])

song_length += 3 # <- 3s

note_margin = 2

note_count = note_highest-note_lowest+note_margin

note_h = screen_height/(note_count+note_margin+1)
zoom = 300

bar_x = screen_width/2

if os.path.exists("res"):
    shutil.rmtree("res")
os.mkdir("res")

font = pygame.font.Font("data/Galmuri7.ttf", 24)
fontb = pygame.font.Font("data/Galmuri11-Bold.ttf", 48)
def draw_text(screen, text, x, y, color=bar_color, font=font):
    render = font.render(text, False, color)
    screen.blit(render, (x, y))

def draw():
    screen.fill(bg_color)
    for i, notes in enumerate(all_notes.values()):
        for note_data in notes:
            note = note_data[0]
            f = (5/(i+1))
            note_x = (note.start-play_time)*zoom/f+bar_x
            note_length = (note.end-note.start)*zoom/f 
            if screen_width > note_x and note_x+note_length > 0:
                a = 0
                color = colors[i]
                if note_x < bar_x:
                    note_data[1] *= 0.9
                    a = note_data[1]
                    if note_x+note_length > bar_x:
                        color = p_colors[i]
                pygame.draw.rect(screen, color, [note_x, (note_count-note.pitch+note_lowest)*note_h-a/2, note_length, note_h/note_slim+a])
                
    pygame.draw.line(screen, bar_color, [bar_x, 0], [bar_x, screen_height], 4)
    
    draw_text(screen, title, 70, 70, font=fontb)
    draw_text(screen, desc, 70, 140)

if preview:
    screen = pygame.display.set_mode((screen_width, screen_height))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        play_time = (pygame.time.get_ticks()-start_time)/1000
        
        draw()
        
        dt = clock.tick(120)*60/1000

        if play_time > song_length:
            print("end")

        pygame.display.update()
else:
    #render
    screen = pygame.Surface((screen_width, screen_height))
    fps = 30
    print(f"rendering | fps: {fps} | frames: {int(fps*song_length)}")
    for frame in range(int(fps*song_length)):
        try:
            play_time = frame/fps-1

            draw()

            pygame.image.save(screen, f"res/{frame}.png")
        except KeyboardInterrupt:
            break

    print("making video")
    video = cv2.VideoWriter(f"{title}.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (screen_width, screen_height))

    for file in sorted(os.listdir("res"), key=len):
        image = cv2.imread(f"res/{file}")
        video.write(image)

    print("video done")
    cv2.destroyAllWindows()
    video.release()
from pico2d import *
import game_world
import game_framework
from boy import Boy
from grass import Grass
from bird import BirdFlock, release_bird_image
from ball import Ball

boy = None
flock = None


def handle_events():


    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)


def init():
    global boy, flock

    game_world.clear()

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)

    flock = BirdFlock(get_canvas_width(), get_canvas_height())
    game_world.add_oject(flock)


def pause():
    boy.pause()


def resume():
    pass


def finish():
    global boy, flock
    game_world.clear()
    boy = None
    flock = None
    release_bird_image()
    Ball.images.clear()


def update():
    game_world.update()

def render():
    clear_canvas()
    game_world.render()
    update_canvas()










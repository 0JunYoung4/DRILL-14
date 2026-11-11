"""실제 SDL 텍스처로 장면과 14개 동작을 렌더링해 .artifacts에 저장한다.

실행: python tools/verify_scene.py
단위 테스트와 달리 창을 열고 실제 리소스 로딩·그리기·종료까지 검증한다.
"""

import json
from ctypes import byref
import os
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pico2d
import pico2d.pico2d as canvas
from sdl2 import (SDL_CreateRGBSurfaceWithFormat, SDL_FreeSurface,
                  SDL_PIXELFORMAT_ARGB8888, SDL_RenderReadPixels,
                  SDL_Event, SDL_PushEvent, SDL_QUIT,
                  SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_ESCAPE)
from sdl2.sdlimage import IMG_SavePNG

from ball import Ball, GRAVITY, LAUNCH_SPEED_Y
from bird import Bird, FRAME_COUNT
import game_framework
import game_world
import play_mode

OUTPUT = ROOT / '.artifacts'


def save_render(name):
    """화면 전송 전의 그리기 버퍼를 저장해 실제 표시 좌표를 검증한다."""
    surface = SDL_CreateRGBSurfaceWithFormat(0, 1600, 600, 32, SDL_PIXELFORMAT_ARGB8888)
    if not surface:
        raise RuntimeError('렌더 검증용 표면을 생성하지 못했습니다.')
    try:
        result = SDL_RenderReadPixels(canvas.renderer, None, surface.contents.format.contents.format,
                                      surface.contents.pixels, surface.contents.pitch)
        if result != 0 or IMG_SavePNG(surface, os.fsencode(OUTPUT / name)) != 0:
            raise RuntimeError('검증용 PNG를 저장하지 못했습니다.')
    finally:
        SDL_FreeSurface(surface)
    pico2d.update_canvas()


def save_scene(name):
    pico2d.clear_canvas()
    game_world.render()
    save_render(name)


def step(dt):
    game_framework.frame_time = dt
    game_world.update()


def event(key, event_type=SDL_KEYDOWN):
    play_mode.boy.handle_event(SimpleNamespace(type=event_type, key=key))


def main():
    os.chdir(ROOT)
    OUTPUT.mkdir(exist_ok=True)
    report = {'bird_count': 10, 'valid_frames': FRAME_COUNT, 'ball_samples': []}
    pico2d.open_canvas(1600, 600)
    try:
        play_mode.init()
        assert len(play_mode.flock.birds) == 10
        save_scene('scene_start.png')

        # 실제 게임 객체와 이벤트 처리로 발사하고 해석해와 비교한다.
        event(SDLK_SPACE)
        projectile = next(obj for obj in game_world.world[1] if isinstance(obj, Ball))
        previous_time = 0.0
        for label, elapsed in (('rising', 0.5), ('apex', LAUNCH_SPEED_Y / GRAVITY), ('falling', 1.5)):
            step(elapsed - previous_time)
            previous_time = elapsed
            assert abs(projectile.x - (400 + 300 * elapsed)) < 0.001
            assert abs(projectile.y - (90 + 300 * elapsed - 0.5 * GRAVITY * elapsed ** 2)) < 0.001
            report['ball_samples'].append(dict(stage=label, t=elapsed, x=projectile.x,
                                               y=projectile.y, vy=projectile.velocity_y))
            save_scene(f'ball_{label}.png')
        step(0.6)
        assert projectile not in game_world.world[1]

        start_x = play_mode.boy.x
        event(SDLK_RIGHT)
        step(0.25)
        event(SDLK_RIGHT, SDL_KEYUP)
        assert play_mode.boy.x > start_x
        event(SDLK_LEFT)
        step(0.25)
        event(SDLK_LEFT, SDL_KEYUP)
        assert abs(play_mode.boy.x - start_x) < 0.001
        assert play_mode.flock.direction == -1
        save_scene('scene_flying_left.png')

        # 양방향 전체 28개 표시에서 옆 프레임 노출·잘림·기준점 이동을 확인한다.
        pico2d.clear_canvas()
        font = pico2d.load_font('ENCR10B.TTF', 18)
        for direction, row_offset in ((1, 0), (-1, 2)):
            for index in range(FRAME_COUNT):
                x = 130 + (index % 7) * 220
                y = 520 - (index // 7 + row_offset) * 140
                sprite = Bird(x, y, image=play_mode.flock.birds[0].image)
                sprite.frame, sprite.face_dir = index, direction
                sprite.draw()
                font.draw(x - 40, y - 47, f'{index + 1:02d} {"R" if direction > 0 else "L"}', (30, 30, 30))
        save_render('all_frames.png')
        play_mode.finish()

        # 같은 캔버스에서 실제 리소스를 다시 로드해 재진입을 확인한다.
        play_mode.init()
        assert len(play_mode.flock.birds) == 10
        assert len(game_world.world[1]) == 2
        save_scene('scene_reentered.png')
        report['scene_reentry'] = 'passed'
        report['boy_movement'] = 'passed'
        report['ball_ground_removal'] = 'passed'

        # 실제 SDL 이벤트 큐와 게임 루프로 두 종료 경로를 각각 통과시킨다.
        play_mode.finish()
        for event_type, name in ((SDL_KEYDOWN, 'esc_exit'), (SDL_QUIT, 'window_close_exit')):
            quit_event = SDL_Event()
            quit_event.type = event_type
            if event_type == SDL_KEYDOWN:
                quit_event.key.keysym.sym = SDLK_ESCAPE
            if SDL_PushEvent(byref(quit_event)) != 1:
                raise RuntimeError('종료 검증용 SDL 이벤트를 추가하지 못했습니다.')
            game_framework.run(play_mode)
            assert not game_framework.running
            assert all(not layer for layer in game_world.world)
            report[name] = 'passed'
    finally:
        play_mode.finish()
        pico2d.close_canvas()
    (OUTPUT / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

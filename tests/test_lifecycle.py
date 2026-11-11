from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import bird
import game_framework
import game_world
import play_mode
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE


class LifecycleTests(unittest.TestCase):
    def test_monotonic_clock_current_delta_and_zero_frame(self):
        times = []
        mode = Mock()
        def update():
            times.append(game_framework.frame_time)
            if len(times) == 3:
                game_framework.quit()
        mode.update.side_effect = update
        with patch('game_framework.time.perf_counter', side_effect=[10, 10, 10, 10.25]):
            game_framework.run(mode)
        self.assertEqual(times, [0.0, 0.0, 0.25])
        mode.finish.assert_called_once()
        self.assertFalse(game_framework.running)

    def test_quit_event_does_not_update_or_render(self):
        mode = Mock()
        mode.handle_events.side_effect = game_framework.quit
        game_framework.run(mode)
        mode.update.assert_not_called()
        mode.render.assert_not_called()
        mode.finish.assert_called_once()

    def test_reenter_scene_has_ten_birds_and_boy(self):
        with patch('play_mode.Boy') as boy, patch('play_mode.Grass'), \
                patch('play_mode.get_canvas_width', return_value=1600), \
                patch('play_mode.get_canvas_height', return_value=600), \
                patch('pico2d.load_image', return_value=Mock()) as loader:
            bird.release_bird_image()
            try:
                for _ in range(2):
                    play_mode.init()
                    self.assertEqual(len(play_mode.flock.birds), 10)
                    self.assertEqual(len(game_world.world[1]), 2)
                    self.assertIn(boy.return_value, game_world.world[1])
                    play_mode.finish()
                    self.assertTrue(all(not layer for layer in game_world.world))
                    self.assertIsNone(play_mode.boy)
                    self.assertIsNone(play_mode.flock)
                    self.assertIsNone(bird._shared_image)
                self.assertEqual(loader.call_count, 2)
            finally:
                play_mode.finish()

    def test_escape_and_window_close_request_quit(self):
        for event in (SimpleNamespace(type=SDL_QUIT),
                      SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_ESCAPE)):
            with patch('play_mode.get_events', return_value=[event]), \
                    patch('game_framework.quit') as quit_game:
                play_mode.handle_events()
                quit_game.assert_called_once()


if __name__ == '__main__':
    unittest.main()

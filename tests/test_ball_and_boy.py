from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE

import ball
import boy
import game_framework
import game_world


class BallTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(game_world.clear)
        game_world.clear()
        images = patch.object(ball.Ball, 'images', {1: Mock(), 2: Mock()})
        images.start()
        self.addCleanup(images.stop)
        width = patch('ball.get_canvas_width', return_value=1600)
        width.start()
        self.addCleanup(width.stop)

    def advance(self, projectile, dt):
        game_framework.frame_time = dt
        projectile.update()

    def test_launch_speeds_and_radii(self):
        for direction in (-1, 1):
            for kind, radius in ((1, 10.5), (2, 20.5)):
                projectile = ball.Ball(400, 90, direction, kind)
                self.assertEqual(projectile.velocity_x, direction * 300)
                self.assertEqual(projectile.velocity_y, 300)
                self.assertEqual(projectile.radius, radius)

    def test_rises_reaches_apex_then_falls(self):
        projectile = ball.Ball(400, 90, 1)
        time_to_apex = ball.LAUNCH_SPEED_Y / ball.GRAVITY
        self.advance(projectile, time_to_apex)
        self.assertAlmostEqual(projectile.velocity_y, 0)
        self.assertAlmostEqual(projectile.y, 90 + 300 ** 2 / (2 * ball.GRAVITY))
        highest = projectile.y
        self.advance(projectile, 0.25)
        self.assertLess(projectile.velocity_y, 0)
        self.assertLess(projectile.y, highest)

    def test_analytic_trajectory_at_different_fps(self):
        for fps in (30, 60, 144):
            projectile = ball.Ball(400, 90, 1)
            for _ in range(fps):
                self.advance(projectile, 1 / fps)
            with self.subTest(fps=fps):
                self.assertAlmostEqual(projectile.x, 700, delta=0.001)
                self.assertAlmostEqual(projectile.y, 90 + 300 - 0.5 * ball.GRAVITY, delta=0.001)
                self.assertAlmostEqual(projectile.velocity_y, 300 - ball.GRAVITY, delta=0.001)

    def test_irregular_steps_match_single_step(self):
        first, second = ball.Ball(800, 90, -1), ball.Ball(800, 90, -1)
        self.advance(first, 1)
        for dt in [0.01, 0.03, 0.06] * 10:
            self.advance(second, dt)
        for field in ('x', 'y', 'velocity_y'):
            self.assertAlmostEqual(getattr(first, field), getattr(second, field), delta=0.001)

    def test_ground_contact_removes_both_sizes(self):
        for kind, radius in ((1, 10.5), (2, 20.5)):
            projectile = ball.Ball(400, ball.GROUND_Y + radius, 1, kind)
            game_world.add_oject(projectile)
            self.advance(projectile, 0)
            self.assertNotIn(projectile, game_world.world[1])

    def test_removal_waits_until_whole_ball_is_outside(self):
        for side in (-1, 1):
            projectile = ball.Ball(0 if side < 0 else 1600, 200, side)
            game_world.add_oject(projectile)
            self.advance(projectile, 0)
            self.assertIn(projectile, game_world.world[1])
            self.advance(projectile, 0.1)
            self.assertNotIn(projectile, game_world.world[1])


class BoyTests(unittest.TestCase):
    def setUp(self):
        game_world.clear()
        self.addCleanup(game_world.clear)
        for name in ('load_image', 'load_font'):
            loader = patch('boy.' + name, return_value=Mock())
            loader.start()
            self.addCleanup(loader.stop)
        clock = patch('boy.get_time', return_value=0)
        clock.start()
        self.addCleanup(clock.stop)
        width = patch('boy.get_canvas_width', return_value=1600)
        width.start()
        self.addCleanup(width.stop)
        self.boy = boy.Boy()

    def event(self, key, event_type=SDL_KEYDOWN):
        self.boy.handle_event(SimpleNamespace(type=event_type, key=key))

    def test_normal_initial_position_and_draw(self):
        self.assertEqual((self.boy.x, self.boy.y, self.boy.state), (400, 90, 'IDLE'))
        self.boy.draw()
        self.boy.image.clip_draw.assert_called_once()

    def test_left_right_movement_and_key_release(self):
        game_framework.frame_time = 0.5
        for key, direction in ((SDLK_LEFT, -1), (SDLK_RIGHT, 1)):
            before = self.boy.x
            self.event(key)
            self.boy.update()
            self.assertAlmostEqual(self.boy.x, before + direction * boy.RUN_SPEED_PPS * 0.5)
            self.assertEqual(self.boy.face_dir, direction)
            self.event(key, SDL_KEYUP)
            self.assertEqual(self.boy.state, 'IDLE')

    def test_idle_animation_uses_seconds(self):
        game_framework.frame_time = 0.5
        self.boy.update()
        self.assertEqual(self.boy.frame, 4)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[0], 400)

    def test_space_fires_in_idle_run_and_sleep(self):
        with patch('boy.Ball') as projectile:
            self.event(SDLK_SPACE)
            projectile.assert_called_with(400, 90, 1, 1)
            self.event(SDLK_LEFT)
            self.event(SDLK_SPACE)
            projectile.assert_called_with(400, 90, -1, 1)
            self.event(SDLK_LEFT, SDL_KEYUP)
            self.boy.fall_asleep()
            self.event(SDLK_SPACE)
            self.assertEqual(self.boy.state, 'IDLE')
            self.assertEqual(projectile.call_count, 3)


if __name__ == '__main__':
    unittest.main()

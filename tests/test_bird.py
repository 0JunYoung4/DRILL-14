import math
import unittest
from unittest.mock import Mock

from bird import (Bird, BirdFlock, FRAME_RECTS, HALF_WIDTH, HALF_HEIGHT,
                  SHEET_WIDTH, SHEET_HEIGHT, DRAW_SCALE, ANCHOR_X, ANCHOR_Y)
from bird_motion import FlightMotion, animation_frame


class FlightTests(unittest.TestCase):
    def simulate(self, steps):
        flock = BirdFlock(image=Mock())
        for dt in steps:
            flock.update(dt)
        return flock

    def assert_same_flight(self, first, second):
        self.assertAlmostEqual(first.x, second.x, delta=0.001)
        self.assertEqual(first.direction, second.direction)
        for a, b in zip(first.birds, second.birds):
            self.assertAlmostEqual(a.x, b.x, delta=0.001)
            self.assertEqual(a.frame, b.frame)
            self.assertEqual(a.face_dir, b.face_dir)

    def test_fps_independence(self):
        for seconds in (1, 10, 100):
            reference = self.simulate([seconds])
            for fps in (30, 60, 144):
                with self.subTest(seconds=seconds, fps=fps):
                    self.assert_same_flight(reference, self.simulate([1 / fps] * (fps * seconds)))

    def test_irregular_time_partition(self):
        steps = [0.013, 0.007, 0.06, 0.02] * 100
        self.assert_same_flight(self.simulate([math.fsum(steps)]), self.simulate(steps))

    def test_exact_boundaries_face_inward(self):
        motion = FlightMotion(5, 0, 10, speed=10)
        motion.advance(0.5)
        self.assertEqual(motion.sample(), (10, -1))
        motion.advance(1)
        self.assertEqual(motion.sample(), (0, 1))

    def test_before_and_after_boundary(self):
        for t, expected_direction in ((0.5 - 1e-6, 1), (0.5, -1), (0.5 + 1e-6, -1)):
            with self.subTest(t=t):
                motion = FlightMotion(5, 0, 10, speed=10)
                motion.advance(t)
                x, direction = motion.sample()
                self.assertLessEqual(x, 10)
                self.assertGreaterEqual(x, 0)
                self.assertEqual(direction, expected_direction)

    def test_overshoot_and_many_round_trips(self):
        motion = FlightMotion(5, 0, 10, speed=10)
        motion.advance(100.75)
        self.assertEqual(motion.sample(), (7.5, -1))

    def test_all_ten_sprites_stay_inside(self):
        flock = BirdFlock(image=Mock())
        for dt in [0, 2.4525, 4.905, 1000.25] + [1 / 60] * 900:
            flock.update(dt)
            for bird in flock.birds:
                self.assertGreaterEqual(bird.x - HALF_WIDTH, -0.001)
                self.assertLessEqual(bird.x + HALF_WIDTH, 1600.001)
                self.assertGreater(bird.y - HALF_HEIGHT, 140)
                self.assertLessEqual(bird.y + HALF_HEIGHT, 600)
                self.assertEqual(bird.face_dir, flock.direction)

    def test_unique_positions_and_shared_image(self):
        image = Mock()
        flock = BirdFlock(image=image)
        self.assertEqual(len(flock.birds), 10)
        self.assertEqual(len({(b.x, b.y) for b in flock.birds}), 10)
        self.assertTrue(all(b.image is image for b in flock.birds))

    def test_invalid_time_and_bounds(self):
        for dt in (-1, math.inf, math.nan):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                FlightMotion(5, 0, 10).advance(dt)
        for args in ((5, 10, 0), (11, 0, 10), (math.nan, 0, 10)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                FlightMotion(*args)
        with self.assertRaises(ValueError):
            BirdFlock(canvas_width=500, image=Mock())

    def test_zero_time_does_not_change_state(self):
        self.assert_same_flight(self.simulate([0]), self.simulate([0, 0, 0]))


class AnimationTests(unittest.TestCase):
    def test_all_frames_and_one_second_cycle(self):
        for index in range(141):
            self.assertEqual(animation_frame(index / 14), index % 14)

    def test_frame_boundary(self):
        self.assertEqual(animation_frame(1 / 14 - 1e-8), 0)
        self.assertEqual(animation_frame(1 / 14), 1)
        self.assertEqual(animation_frame(1 / 14 + 1e-8), 1)

    def test_direction_change_keeps_animation_time(self):
        flock = BirdFlock(image=Mock())
        until_edge = (flock.motion.right - flock.x) / flock.motion.speed
        flock.update(until_edge)
        self.assertEqual(flock.direction, -1)
        for bird in flock.birds:
            self.assertEqual(bird.frame, animation_frame(until_edge, bird.phase))
        flock.update(0.2)
        for bird in flock.birds:
            self.assertEqual(bird.frame, animation_frame(until_edge + 0.2, bird.phase))

    def test_rectangles_exclude_blank_and_stay_in_sheet(self):
        self.assertEqual(len(FRAME_RECTS), 14)
        for x, y, w, h in FRAME_RECTS:
            self.assertLessEqual(x + w, SHEET_WIDTH)
            self.assertLessEqual(y + h, SHEET_HEIGHT)
            self.assertGreater(w * h, 0)
        self.assertNotIn((728, 344, 182, 162), FRAME_RECTS)

    def test_draw_preserves_anchor_scale_and_flip_for_every_frame(self):
        image = Mock()
        bird = Bird(400, 450, image=image)
        for frame, (_, top, width, height) in enumerate(FRAME_RECTS):
            for direction in (1, -1):
                bird.frame, bird.face_dir = frame, direction
                bird.draw()
                args = image.clip_composite_draw.call_args.args
                self.assertEqual(args[1], SHEET_HEIGHT - top - height)
                self.assertEqual(args[5], 'h' if direction < 0 else '')
                self.assertEqual(args[8:], (width * DRAW_SCALE, height * DRAW_SCALE))
                anchor_x = args[6] + direction * (ANCHOR_X - width / 2) * DRAW_SCALE
                anchor_y = args[7] - (ANCHOR_Y - height / 2) * DRAW_SCALE
                self.assertEqual((anchor_x, anchor_y), (400, 450))


if __name__ == '__main__':
    unittest.main()

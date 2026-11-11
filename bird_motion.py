"""렌더링에 의존하지 않는 초 단위 비행 계산."""

import math


FLIGHT_SPEED_PPS = 200.0


class FlightMotion:
    def __init__(self, start_x, speed=FLIGHT_SPEED_PPS):
        if not math.isfinite(speed) or speed <= 0:
            raise ValueError('비행 속도는 양의 유한수여야 합니다.')
        self.start_x = start_x
        self.speed = speed
        self.elapsed = 0.0
        self._time_error = 0.0

    def advance(self, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError('경과 시간은 0 이상의 유한수여야 합니다.')
        # Kahan 합산으로 1/30, 1/60 등의 반복 누적 오차를 줄인다.
        corrected = dt - self._time_error
        total = self.elapsed + corrected
        self._time_error = (total - self.elapsed) - corrected
        self.elapsed = total

    def sample(self):
        return self.start_x + self.speed * self.elapsed, 1

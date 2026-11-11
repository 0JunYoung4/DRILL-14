"""렌더링에 의존하지 않는 초 단위 비행 계산."""

import math


FLIGHT_SPEED_PPS = 200.0
ANIMATION_FPS = 14.0


def animation_frame(elapsed, initial_phase=0.0, fps=ANIMATION_FPS, frame_count=14):
    """위상은 프레임 단위다. 정수 경계의 부동소수점 오차만 보정한다."""
    phase = elapsed * fps + initial_phase
    nearest_frame = round(phase)
    if math.isclose(phase, nearest_frame, rel_tol=0.0, abs_tol=1e-10):
        phase = nearest_frame
    return math.floor(phase) % frame_count


class FlightMotion:
    def __init__(self, start_x, left=0.0, right=1600.0, speed=FLIGHT_SPEED_PPS):
        if not math.isfinite(speed) or speed <= 0:
            raise ValueError('비행 속도는 양의 유한수여야 합니다.')
        if (not all(math.isfinite(value) for value in (start_x, left, right))
                or right <= left or not left <= start_x <= right):
            raise ValueError('시작 위치와 비행 경계를 확인하세요.')
        self.start_x = start_x
        self.left = left
        self.right = right
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
        length = self.right - self.left
        period = 2 * length
        distance = self.start_x - self.left + self.speed * self.elapsed
        phase = distance % period
        # 산술 오차 때문에 정확한 경계에서 방향이 한 프레임 늦게 바뀌지 않게 한다.
        nearest_edge = round(phase / length) * length
        if math.isclose(phase, nearest_edge, rel_tol=0.0, abs_tol=1e-9):
            phase = nearest_edge % period
        if phase < length:
            return self.left + phase, 1
        return self.right - (phase - length), -1

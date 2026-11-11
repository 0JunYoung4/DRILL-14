"""새 스프라이트와 무리 비행. 이미지 좌표는 원본의 왼쪽 위 기준이다."""

from pathlib import Path


SHEET_WIDTH = 918
SHEET_HEIGHT = 506
# 실제 그림 간격은 182 × 172이다. 끝의 투명 여백과 빈 15번 칸은 제외한다.
# 마지막 행은 원본 아래쪽에서 잘린 투명 여백만큼 높이가 짧다.
FRAME_RECTS = (
    (0, 0, 182, 172),
    (182, 0, 182, 172),
    (364, 0, 182, 172),
    (546, 0, 182, 172),
    (728, 0, 182, 172),
    (0, 172, 182, 172),
    (182, 172, 182, 172),
    (364, 172, 182, 172),
    (546, 172, 182, 172),
    (728, 172, 182, 172),
    (0, 344, 182, 162),
    (182, 344, 182, 162),
    (364, 344, 182, 162),
    (546, 344, 182, 162),
)
FRAME_COUNT = len(FRAME_RECTS)
DRAW_SCALE = 0.5
# 매 프레임의 몸통 부근을 같은 월드 좌표에 놓는다.
ANCHOR_X = 104
ANCHOR_Y = 100
HALF_WIDTH = max(ANCHOR_X, 182 - ANCHOR_X) * DRAW_SCALE
HALF_HEIGHT = max(ANCHOR_Y, 172 - ANCHOR_Y) * DRAW_SCALE

_shared_image = None


def get_bird_image():
    """같은 플레이 모드의 모든 새가 한 SDL 텍스처를 공유한다."""
    global _shared_image
    if _shared_image is None:
        from pico2d import load_image
        _shared_image = load_image(str(Path(__file__).with_name('bird_animation.png')))
    return _shared_image


def release_bird_image():
    """월드에서 새를 제거한 뒤, 캔버스를 닫기 전에 공유 참조를 해제한다."""
    global _shared_image
    _shared_image = None


class Bird:
    """개별 새의 표시 상태. 시간 진행은 무리에서 한 번만 담당한다."""

    def __init__(self, x, y, phase=0.0, image=None):
        self.x = x
        self.y = y
        self.phase = phase
        self.frame = 0
        self.face_dir = 1
        self.image = image if image is not None else get_bird_image()

    def draw(self):
        left, top, width, height = FRAME_RECTS[self.frame]
        bottom = SHEET_HEIGHT - top - height
        # 좌우 반전 때에도 몸통 기준점을 유지한다. 마지막 행의 짧은 높이를
        # 늘리지 않고 같은 배율로 그려 날개와 몸통이 위아래로 튀지 않게 한다.
        x = self.x + self.face_dir * (width / 2 - ANCHOR_X) * DRAW_SCALE
        y = self.y + (ANCHOR_Y - height / 2) * DRAW_SCALE
        self.image.clip_composite_draw(
            left, bottom, width, height, 0,
            'h' if self.face_dir < 0 else '',
            x, y, width * DRAW_SCALE, height * DRAW_SCALE,
        )

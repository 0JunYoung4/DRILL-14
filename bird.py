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

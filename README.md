# Drill 14: 새 10마리의 비행 애니메이션

`bird_animation.png`의 14개 동작으로 새 10마리가 좌우 왕복 비행한다. 실행 FPS와 무관하게 초당 200픽셀 이동하고, 초당 14개 동작으로 날갯짓한다. 소년은 기존 장면에 함께 표시되며 공을 위로 발사할 수 있다.

## 실행

Windows, Python 3.10에서 검증했다. 프로젝트 폴더에서 실행한다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

| 입력 | 동작 |
| --- | --- |
| ← / → | 소년의 좌우 이동 |
| 스페이스 | 바라보는 방향으로 공 발사. 잠들어 있으면 일어나면서 발사 |
| ESC / 창 닫기 | 종료 |

소년은 기존 동작대로 5초 동안 가만히 있으면 잠든다. 공은 수평·위쪽 초기 속도 300픽셀/초로 발사되어 중력에 따라 떨어지고, 지면에 닿거나 화면 밖으로 완전히 나가면 제거된다.

## 검증

```powershell
python -m unittest discover -s tests -v
python tools/verify_scene.py
```

첫 명령은 창을 열지 않는 자동 테스트 28개를 실행한다. 두 번째 명령은 실제 SDL 창과 이미지로 그리기·소년 이동·공 궤적·장면 재진입·종료 이벤트를 검증한 뒤 창을 닫는다. 생성한 PNG와 수치 결과는 Git에서 제외한 `.artifacts/`에 저장된다.

계획은 [PRD.md](PRD.md), 검증 결과는 [VERIFICATION.md](VERIFICATION.md)에 기록했다. 최종 커밋 본문에서도 구현 수식과 검증 결과를 확인할 수 있다.

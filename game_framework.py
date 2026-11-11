import time
running = False
stack = []


def change_mode(mode):
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    if stack:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    if stack:
        stack.pop().finish()
    if stack:
        stack[-1].resume()
    else:
        quit()


def quit():
    global running
    running = False

frame_time = 0.0

def run(start_mode):
    global running, stack, frame_time
    running = True
    stack = [start_mode]

    try:
        start_mode.init()
        frame_time = 0.0
        previous_time = time.perf_counter()
        first_frame = True
        while running:
            current_time = time.perf_counter()
            # 업데이트 전에 이번 경과 시간을 확정한다. 초기 로딩 시간은 제외한다.
            frame_time = 0.0 if first_frame else current_time - previous_time
            first_frame = False
            previous_time = current_time
            stack[-1].handle_events()
            if not running:
                break
            stack[-1].update()
            stack[-1].render()
    finally:
        while stack:
            stack.pop().finish()
        running = False

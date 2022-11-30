"""
디버깅 유틸 함수
"""
import time


# 실행 시간을 확인하길 원하는 함수에 annotation 으로 붙이면 터미널에 실행시간 뜸
def logging_time(original_fn):
    """
    실행 시간 확인
    """

    def wrapper_(*args, **kwargs):
        """
        wrapper
        """
        start_time = time.time()
        result = original_fn(*args, **kwargs)
        end_time = time.time()
        print(f"WorkingTime[{original_fn.__name__}]: {end_time - start_time} sec")
        return result

    return wrapper_

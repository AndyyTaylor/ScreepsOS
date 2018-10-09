
def main_func(param: int) -> int:
    return param + 1


def test_main_run() -> None:
    assert(main_func(5) == 6)

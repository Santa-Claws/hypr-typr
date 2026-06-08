import sys


def main() -> None:
    args = sys.argv[1:]
    cmd = args[0] if args else "settings"

    if cmd == "type":
        from .engine import run_type_clipboard
        run_type_clipboard()
    elif cmd == "stop":
        from .engine import run_stop
        run_stop()
    elif cmd == "settings":
        from .tui import run_tui
        run_tui()
    else:
        print(f"Usage: hypr-typr [type|stop|settings]")
        sys.exit(1)


if __name__ == "__main__":
    main()

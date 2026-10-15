"""python -m server"""

from __future__ import annotations

import argparse
import webbrowser

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="PhoneSploit Pro web console")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address. Default is localhost only.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print("Warning: the console has no authentication. Binding beyond localhost exposes device control.")
    url = f"http://{args.host}:{args.port}"
    print(f"PhoneSploit web console at {url}")
    if not args.no_browser:
        webbrowser.open(url)
    uvicorn.run("server.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()

import subprocess
import sys
import time
import socket
from pathlib import Path

try:
    from pyngrok import ngrok
except Exception:
    ngrok = None


NGROK_AUTH_TOKEN = "3CaUOUB1HX1KU4TZ0vW8Kk8LdZR_7CUGtjSTVSxWicmtWcqvr"
PORT = 8501
APP_FILE = "dash_sunat.py"


def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _resolve_port() -> int:
    cli_port = None
    if len(sys.argv) > 2:
        try:
            cli_port = int(sys.argv[2])
        except ValueError as exc:
            raise ValueError("El puerto debe ser numerico. Ejemplo: python run_public_sunat.py dash_sunat.py 8502") from exc

    base_port = cli_port or PORT
    for candidate in range(base_port, base_port + 30):
        if _is_port_free(candidate):
            return candidate
    raise RuntimeError(f"No se encontro puerto libre desde {base_port} hasta {base_port + 29}.")


def _resolve_app_file() -> str:
    cli_arg = sys.argv[1] if len(sys.argv) > 1 else None
    app_candidate = cli_arg or APP_FILE
    app_path = Path(app_candidate)
    if not app_path.exists():
        raise FileNotFoundError(f"No se encontro la app de Streamlit: {app_candidate}")
    return str(app_path)


def _check_streamlit() -> None:
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        raise RuntimeError(
            "No se encontro Streamlit en este entorno. Instala dependencias con: "
            f'"{sys.executable}" -m pip install -r requirements.txt'
        ) from exc


def main() -> None:
    _check_streamlit()
    app_file = _resolve_app_file()
    port = _resolve_port()

    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_file,
        "--server.port",
        str(port),
    ]
    streamlit_proc = subprocess.Popen(streamlit_cmd)

    time.sleep(3)
    if streamlit_proc.poll() is not None:
        raise RuntimeError("Streamlit no inicio. Revisa el error mostrado en consola.")

    print(f"App ejecutada: {app_file}")
    print(f"Dashboard local: http://localhost:{port}")

    public_url = None
    token = NGROK_AUTH_TOKEN.strip()
    if ngrok and token and token != "PEGA_AQUI_TU_TOKEN":
        try:
            ngrok.set_auth_token(token)
            try:
                tunnel = ngrok.connect(port)
            except Exception as exc:
                if "ERR_NGROK_334" in str(exc) or "already online" in str(exc):
                    print("Endpoint ngrok ya activo; reintentando con pooling_enabled=True...")
                    tunnel = ngrok.connect(port, pooling_enabled=True)
                else:
                    raise
            public_url = tunnel.public_url
            print(f"URL publica: {public_url}")
        except Exception as exc:
            print(f"No se pudo crear URL publica (ngrok): {exc}")
    else:
        print("URL publica deshabilitada (pyngrok o token no disponible).")

    print("Presiona Ctrl + C para cerrar.")

    try:
        streamlit_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if ngrok and public_url:
            try:
                ngrok.disconnect(public_url)
            except Exception:
                pass
        if streamlit_proc.poll() is None:
            streamlit_proc.terminate()


if __name__ == "__main__":
    main()

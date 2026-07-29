import io
import socket
import threading

try:
    from flask import Flask, request, Response
    FLASK_DISPONIVEL = True
except Exception:
    FLASK_DISPONIVEL = False

try:
    import qrcode
    QRCODE_DISPONIVEL = True
except Exception:
    QRCODE_DISPONIVEL = False

try:
    from pyngrok import ngrok
    NGROK_DISPONIVEL = True
except Exception:
    NGROK_DISPONIVEL = False

try:
    import pygame
except Exception:
    pygame = None

_lock = threading.Lock()

_estado_movimento = {
    "esquerda": False,
    "direita": False,
    "agachar": False,
}

_eventos_pendentes = []  # ações "de um clique só": pular, atacar

_flask_app = None
_thread_flask = None
_flask_iniciado = False
_url_atual = None
_celular_conectado = False
_ultimo_ping = 0.0


PAGINA_HTML = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Controle - As Sete Velas</title>
<style>
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; user-select: none; }
  html, body {
    margin: 0; padding: 0; height: 100%;
    background: #0a0519; color: #e6d9b8;
    font-family: Georgia, 'Times New Roman', serif;
    overscroll-behavior: none; touch-action: none;
  }
  h1 {
    text-align: center; font-size: 20px; margin: 14px 0 2px 0;
    color: #ffdc50; letter-spacing: 1px;
  }
  .status {
    text-align: center; font-size: 13px; color: #a89870; margin-bottom: 10px;
  }
  .status.ok { color: #7bd88f; }
  .area {
    display: flex; justify-content: space-between; align-items: flex-end;
    height: calc(100% - 70px); padding: 10px 18px 26px 18px;
  }
  .dpad {
    display: grid;
    grid-template-columns: 70px 70px;
    grid-template-rows: 70px 70px;
    gap: 10px;
  }
  .dpad .btn { grid-row: 2; }
  .dpad .esquerda { grid-column: 1; }
  .dpad .direita { grid-column: 2; }
  .dpad .agachar { grid-column: 1 / span 2; grid-row: 1; height: 46px; }

  .acoes {
    display: flex; flex-direction: column; gap: 16px; align-items: center;
  }

  .btn {
    background: rgba(200,160,50,0.18);
    border: 2px solid #c8a032;
    border-radius: 14px;
    color: #ffdc50;
    font-size: 26px;
    font-weight: bold;
    display: flex; align-items: center; justify-content: center;
    width: 78px; height: 78px;
    touch-action: none;
  }
  .btn:active, .btn.pressionado {
    background: #ffd700;
    color: #241a05;
    border-color: #ffe680;
  }
  .btn.pular { width: 90px; height: 90px; border-radius: 50%; }
  .btn.atacar { width: 90px; height: 90px; border-radius: 50%; border-color: #d05a4a; color: #ff9a86; }
  .btn.atacar:active, .btn.atacar.pressionado { background: #e04b34; color: #fff; }
  .rodape { text-align: center; font-size: 11px; color: #6b5f45; padding-bottom: 6px; }
</style>
</head>
<body>
  <h1>As Sete Velas &mdash; Controle</h1>
  <div class="status" id="status">conectando...</div>

  <div class="area">
    <div class="dpad">
      <div class="btn agachar" data-acao="agachar">AGACHAR</div>
      <div class="btn esquerda" data-acao="esquerda">&#8592;</div>
      <div class="btn direita" data-acao="direita">&#8594;</div>
    </div>
    <div class="acoes">
      <div class="btn pular" data-evento="pular">PULAR</div>
      <div class="btn atacar" data-evento="atacar">ATACAR</div>
    </div>
  </div>
  <div class="rodape">mantenha esta aba aberta enquanto joga</div>

<script>
function enviarMovimento(dados) {
  fetch("/mover", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(dados)
  }).catch(() => {});
}
function enviarEvento(nome) {
  fetch("/acao", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({nome})
  }).catch(() => {});
}

document.querySelectorAll(".btn[data-acao]").forEach(function (el) {
  var acao = el.getAttribute("data-acao");
  var pressionar = function (ev) {
    ev.preventDefault();
    el.classList.add("pressionado");
    var dados = {};
    dados[acao] = true;
    enviarMovimento(dados);
  };
  var soltar = function (ev) {
    ev.preventDefault();
    el.classList.remove("pressionado");
    var dados = {};
    dados[acao] = false;
    enviarMovimento(dados);
  };
  el.addEventListener("touchstart", pressionar);
  el.addEventListener("touchend", soltar);
  el.addEventListener("touchcancel", soltar);
  el.addEventListener("mousedown", pressionar);
  el.addEventListener("mouseup", soltar);
  el.addEventListener("mouseleave", soltar);
});

document.querySelectorAll(".btn[data-evento]").forEach(function (el) {
  var nome = el.getAttribute("data-evento");
  var disparar = function (ev) {
    ev.preventDefault();
    el.classList.add("pressionado");
    enviarEvento(nome);
    setTimeout(function () { el.classList.remove("pressionado"); }, 120);
  };
  el.addEventListener("touchstart", disparar);
  el.addEventListener("mousedown", disparar);
});

// Ping periódico só para mostrar "conectado" na tela do celular
function marcarStatus(ok) {
  var s = document.getElementById("status");
  if (ok) { s.textContent = "conectado ao jogo"; s.className = "status ok"; }
  else { s.textContent = "sem resposta do jogo..."; s.className = "status"; }
}
setInterval(function () {
  fetch("/status").then(function (r) { return r.json(); })
    .then(function (d) { marcarStatus(true); })
    .catch(function () { marcarStatus(false); });
}, 2000);
marcarStatus(true);
</script>
</body>
</html>
"""


def _criar_app():
    app = Flask(__name__)

    @app.route("/")
    def _pagina():
        return Response(PAGINA_HTML, mimetype="text/html")

    @app.route("/mover", methods=["POST"])
    def _mover():
        global _celular_conectado
        dados = request.get_json(force=True, silent=True) or {}
        with _lock:
            for chave in ("esquerda", "direita", "agachar"):
                if chave in dados:
                    _estado_movimento[chave] = bool(dados[chave])
            _celular_conectado = True
        return ("", 204)

    @app.route("/acao", methods=["POST"])
    def _acao():
        global _celular_conectado
        dados = request.get_json(force=True, silent=True) or {}
        nome = dados.get("nome")
        if nome in ("pular", "atacar"):
            with _lock:
                _eventos_pendentes.append(nome)
                _celular_conectado = True
        return ("", 204)

    @app.route("/status")
    def _status():
        return {"ok": True}

    return app


def _rodar_flask(porta):
    global _flask_app
    _flask_app = _criar_app()
    _flask_app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False)


def _obter_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def dependencias_ok():
    """Retorna (ok, mensagem) dizendo se dá pra usar o servidor mobile."""
    if not FLASK_DISPONIVEL:
        return False, "Falta instalar: pip install flask"
    return True, ""


def iniciar_servidor(porta=5000, usar_ngrok=True):
    """
    Garante que o servidor Flask esteja rodando (idempotente) e devolve a
    URL para acessar o controle: pública via ngrok se disponível/pedida,
    senão o IP local da máquina na rede.
    """
    global _thread_flask, _flask_iniciado, _url_atual

    if not FLASK_DISPONIVEL:
        return None

    if not _flask_iniciado:
        _thread_flask = threading.Thread(target=_rodar_flask, args=(porta,), daemon=True)
        _thread_flask.start()
        _flask_iniciado = True

    if _url_atual:
        return _url_atual

    if usar_ngrok and NGROK_DISPONIVEL:
        try:
            tunel = ngrok.connect(porta, "http")
            _url_atual = tunel.public_url
            return _url_atual
        except Exception as e:
            print(f"[controle mobile] não foi possível abrir túnel ngrok: {e}")

    ip_local = _obter_ip_local()
    _url_atual = f"http://{ip_local}:{porta}"
    return _url_atual


def parar_tunel():
    """Desconecta o túnel ngrok (o servidor Flask local continua de pé)."""
    global _url_atual
    if NGROK_DISPONIVEL:
        try:
            ngrok.kill()
        except Exception:
            pass
    _url_atual = None


def gerar_superficie_qrcode(url, tamanho=240):
    """Gera o QR code do link como pygame.Surface. Retorna None se faltar libs."""
    if not QRCODE_DISPONIVEL or pygame is None:
        return None
    try:
        img = qrcode.make(url).convert("RGB").resize((tamanho, tamanho))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return pygame.image.load(buffer, "qrcode.png").convert()
    except Exception as e:
        print(f"[controle mobile] erro ao gerar QR code: {e}")
        return None


def obter_estado_movimento():
    """Estado contínuo (mantido pressionado) do controle do celular."""
    with _lock:
        return dict(_estado_movimento)


def consumir_eventos():
    """Ações de disparo único (pular/atacar), consumidas a cada chamada."""
    global _eventos_pendentes
    with _lock:
        eventos, _eventos_pendentes[:] = list(_eventos_pendentes), []
    return eventos


def celular_esta_conectado():
    with _lock:
        return _celular_conectado

"""Pruebas de la lógica pura de reproducción de pasos (sin abrir ventana)."""

from gui.animacion import ControladorAnimacion, VELOCIDADES


class MaestroFalso:
    """Reemplaza a Tkinter para probar ``after`` sin ventana."""

    def __init__(self):
        self.programados = []
        self.cancelados = []

    def after(self, milisegundos, callback):
        self.programados.append((milisegundos, callback))
        return f"after-{len(self.programados)}"

    def after_cancel(self, identificador):
        self.cancelados.append(identificador)


def test_indice_inicial_en_el_ultimo_paso():
    control = ControladorAnimacion(pasos=["a", "b", "c"])

    assert control.total == 3
    assert control.indice == 2
    assert control.paso_actual == "c"


def test_navegacion_y_limites():
    control = ControladorAnimacion(pasos=[0, 1, 2])

    assert control.siguiente() is False
    assert control.anterior() is True
    assert control.indice == 1
    assert control.paso_actual == 1

    control.reiniciar()
    assert control.indice == 0
    assert control.anterior() is False

    control.ir_a(99)
    assert control.indice == 2
    control.ir_a(-5)
    assert control.indice == 0


def test_configurar_vacio_y_reemplazar_pasos():
    control = ControladorAnimacion(pasos=[1, 2])
    assert control.indice == 1

    control.configurar([])
    assert control.total == 0
    assert control.indice == -1
    assert control.paso_actual is None

    control.configurar(["nuevo"], inicial="primero")
    assert control.indice == 0
    assert control.paso_actual == "nuevo"


def test_notifica_cada_cambio():
    vistos = []
    control = ControladorAnimacion(pasos=[10, 20, 30], al_cambiar=vistos.append)

    assert vistos == [2]
    control.reiniciar()
    assert vistos[-1] == 0
    control.siguiente()
    assert vistos[-1] == 1
    control.anterior()
    assert vistos[-1] == 0


def test_reproducir_usa_after_y_avanza():
    maestro = MaestroFalso()
    control = ControladorAnimacion(maestro=maestro, pasos=[0, 1, 2], intervalo=25)
    control.reiniciar()

    assert control.reproducir() is True
    assert control.reproduciendo is True
    assert maestro.programados[-1][0] == 25

    _milisegundos, callback = maestro.programados[-1]
    callback()

    assert control.indice == 1
    assert control.reproduciendo is True
    assert len(maestro.programados) >= 2

    control.pausar()
    assert control.reproduciendo is False
    assert maestro.cancelados


def test_al_terminar_en_el_ultimo_paso():
    maestro = MaestroFalso()
    terminado = []
    control = ControladorAnimacion(
        maestro=maestro,
        pasos=[0, 1],
        al_terminar=lambda: terminado.append(True),
    )
    control.reiniciar()
    control.reproducir()

    _milisegundos, callback = maestro.programados[-1]
    callback()

    assert control.indice == 1
    assert control.reproduciendo is False
    assert terminado == [True]


def test_velocidades():
    control = ControladorAnimacion(pasos=[0, 1])

    for nombre, intervalo in VELOCIDADES.items():
        assert control.set_velocidad(nombre) == intervalo
        assert control.intervalo == intervalo

    assert control.set_velocidad("inexistente") == VELOCIDADES["Normal"]


def test_reproducir_sin_pasos_o_un_solo_paso():
    vacio = ControladorAnimacion()
    assert vacio.reproducir() is False

    unico = ControladorAnimacion(pasos=["solo"])
    assert unico.reproducir() is False


def test_alternar_reproduce_y_pausa():
    maestro = MaestroFalso()
    control = ControladorAnimacion(maestro=maestro, pasos=[0, 1], intervalo=10)
    control.reiniciar()

    assert control.alternar() is True
    assert control.reproduciendo is True
    assert control.alternar() is False
    assert control.reproduciendo is False

class SysDeptError(Exception):
    pass

class ProyectoNoEncontrado(SysDeptError):
    pass

class AgenteNoDisponible(SysDeptError):
    pass

class ErrorExtraccionPDF(SysDeptError):
    pass

class LimiteArchivoExcedido(SysDeptError):
    pass

class RolNoPermitido(SysDeptError):
    pass

class ExtensionNoPermitida(SysDeptError):
    pass

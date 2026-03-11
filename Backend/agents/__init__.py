from agents.agente_lider import AgenteLider
from agents.agente_arquitecto import AgenteArquitecto
from agents.agente_backend import AgenteBackend
from agents.agente_frontend import AgenteFrontend
from agents.agente_qa import AgenteQA
from agents.agente_dba import AgenteDBA
from models.agente import RolAgente, Agente

FABRICA_AGENTES = {
    RolAgente.LIDER: AgenteLider,
    RolAgente.ARQUITECTO: AgenteArquitecto,
    RolAgente.BACKEND: AgenteBackend,
    RolAgente.FRONTEND: AgenteFrontend,
    RolAgente.QA: AgenteQA,
    RolAgente.DBA: AgenteDBA,
}


def crear_agente_instancia(agente: Agente):
    """Crea la instancia correcta de agente según su rol."""
    clase = FABRICA_AGENTES.get(agente.rol)
    if not clase:
        raise ValueError(f"Rol desconocido: {agente.rol}")
    return clase(agente)

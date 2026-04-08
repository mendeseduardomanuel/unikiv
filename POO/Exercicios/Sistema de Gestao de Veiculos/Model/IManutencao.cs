using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestao_de_Veiculos.Model
{
    public interface IManutencao
    {
        void Agendar(DateTime data);
        void RealizarManutencao();
        List<Manutencao> ObterHistorico();
    }
}

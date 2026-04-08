using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestao_de_Veiculos.Model
{
    public class Automovel : Veiculo
    {
        public int NumPortas { get; set; }
        public string TipoCombustivel { get; set; }
        public int NumPassageiros { get; set; }
        public override string GetTipo() => "Automóvel";
    }

}

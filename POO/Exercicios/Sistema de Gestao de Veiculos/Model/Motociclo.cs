using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestao_de_Veiculos.Model
{
    public class Motociclo : Veiculo
    {
        public int Cilindrada { get; set; }
        public bool TemSideCar { get; set; }
        public override string GetTipo() => "Motociclo";
    }
}

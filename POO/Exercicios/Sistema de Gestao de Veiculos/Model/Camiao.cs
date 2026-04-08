using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestao_de_Veiculos.Model
{
    public class Camiao : Veiculo
    {
        public double CapacidadeCarga { get; set; }
        public int NumEixos { get; set; }
        public override string GetTipo() => "Camião";
    }
}

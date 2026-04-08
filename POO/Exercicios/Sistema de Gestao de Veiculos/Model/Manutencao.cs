using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestao_de_Veiculos.Model
{
    public class Manutencao
    {
        public int Id { get; set; }
        public DateTime Data { get; set; }
        public string Tipo { get; set; }
        public string Descricao { get; set; }
        public double Custo { get; set; }
        public double Km { get; set; }
    }
}

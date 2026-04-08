using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public class Transaccao
    {
        public int Id { get; set; }
        public DateTime Data { get; set; }
        public double Valor { get; set; }
        public TipoTransaccao Tipo { get; set; }
        public string Descricao { get; set; }
    }
}

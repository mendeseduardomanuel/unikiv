using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public class ContaOrdem : ContaBancaria
    {
        public double LimiteDescoberto { get; set; }

        public override double CalcularJuros()
        {
            return Saldo * 0.01;
        }
    }
}

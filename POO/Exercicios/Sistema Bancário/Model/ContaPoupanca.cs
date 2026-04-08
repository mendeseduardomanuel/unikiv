using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public class ContaPoupanca : ContaBancaria
    {
        public double TaxaJuroAnual { get; set; }

        public override double CalcularJuros()
        {
            return Saldo * TaxaJuroAnual;
        }
    }
}

using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_Bancário.Model
{
    public class ContaCorrente : ContaBancaria
    {
        public double LimiteCredito { get; set; }
        public double ComissaoMensal { get; set; }

        public override double CalcularJuros()
        {
            return Saldo * 0.02;
        }

        public void CobrarComissao()
        {
            Saldo -= ComissaoMensal;
        }
    }
}

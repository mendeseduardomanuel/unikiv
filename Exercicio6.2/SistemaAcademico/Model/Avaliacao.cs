using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAcademico.Model
{
    public abstract class Avaliacao:IAvaliavel
    {
        public double Nota { get; set; }
        public double Peso { get; set; }

        public Avaliacao(double nota, double peso) 
        { 
            this.Nota= nota;
            this.Peso= peso;                                
        }

        public abstract double CalcularNotaFinal();
    }
}

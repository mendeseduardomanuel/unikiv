using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAcademico.Model
{
    public class ExameFinal:Avaliacao
    {
        public ExameFinal(double nota):base(nota,0.3) { }

        public override double CalcularNotaFinal()
        {
            return Nota * Peso;
        }
    }
}

using System;
using System.Collections.Generic;
using System.Text;

namespace Plataforma_de_Ensino_Online__E_Learning_.Model
{
    public class Inscricao
    {
        public DateTime DataInscricao { get; set; }
        public double NotaFinal { get; set; }

        public Estudante Estudante { get; set; }
        public Curso Curso { get; set; }
    }
}

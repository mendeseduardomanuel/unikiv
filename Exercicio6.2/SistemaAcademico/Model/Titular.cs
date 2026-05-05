using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAcademico.Model
{
    public class Titular:Docente
    {
        public Titular(string nome, int idade):base(nome,idade) { }
    }
}

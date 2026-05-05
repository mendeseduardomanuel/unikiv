using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAcademico.Model
{
    public class Estudante:Pessoa
    {
        public int NumM {  get; set; }

        public Estudante(string nome, int idade, int numM) : base(nome, idade)
        {
            this.NumM = numM;
        }
    }
}

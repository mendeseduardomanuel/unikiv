using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Escolar_Simples.Model
{
    internal class Turma
    {
        public string Codigo { get; set; }
        public int Ano { get; set; }
        public int Capacidade { get; set; }

        private List<Aluno> alunos;
        public Professor Professor { get; set; }

        public Turma(string codigo, int ano, int capacidade)
        {
            Codigo = codigo;
            Ano = ano;
            Capacidade = capacidade;
            alunos = new List<Aluno>();
        }

        public void AdicionarAluno(Aluno aluno)
        {
            if (alunos.Count < Capacidade)
            {
                alunos.Add(aluno);
            }
        }

        public List<Aluno> ListarAlunos()
        {
            return alunos;
        }
    }
}

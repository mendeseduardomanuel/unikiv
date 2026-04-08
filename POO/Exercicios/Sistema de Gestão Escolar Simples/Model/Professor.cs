using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Escolar_Simples.Model
{
    internal class Professor:Pessoa
    {
        private string especialidade { get; set; }
        private string departamento { get; set; }
        private double salario { get; set; }

        public Professor(string nome, DateTime dataNascimento, string telefone,
                         string especialidade, string departamento, double salario)
            : base(nome, dataNascimento, telefone)
        {
            this.especialidade = especialidade;
            this.departamento = departamento;
            this.salario = salario;
        }

        public void Leccionar()
        {
            Console.WriteLine("Professor a leccionar...");
        }

        public double AvaliarAluno(Aluno a)
        {
            return a.CalcularMedia();
        }
    }
}

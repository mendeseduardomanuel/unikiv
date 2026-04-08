using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Escolar_Simples.Model
{
    public class Aluno:Pessoa
    {
        private int numero { get; set; }
        private string curso { get; set; }
        private List<double> notas = new List<double>();

        public Aluno(string nome, DateTime dataNascimento, string telefone, int numero, string curso)
            : base(nome, dataNascimento, telefone)
        {
            this.numero = numero;
            this.curso = curso;
        }

        public void AdicionarNota(double n)
        {
            notas.Add(n);
        }

        public double CalcularMedia()
        {
            return notas.Count == 0 ? 0 : notas.Average();
        }

        public string ObterSituacao()
        {
            return CalcularMedia() >= 10 ? "Aprovado" : "Reprovado";
        }
    }
}

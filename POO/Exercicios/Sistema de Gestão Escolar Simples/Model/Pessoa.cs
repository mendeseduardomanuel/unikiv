using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestão_Escolar_Simples.Model
{
    public class Pessoa
    {
        public string nome { get; set; }
        public DateTime dataNascimento { get; set; }
        public string telefone { get; set; }

        public Pessoa(string nome, DateTime dataNascimento, string telefone)
        {
            this.nome = nome;
            this.dataNascimento = dataNascimento;
            this.telefone = telefone;
        }

        public string GetNome() => nome;

        public int GetIdade()
        {
            return DateTime.Now.Year - dataNascimento.Year;
        }
    }
}

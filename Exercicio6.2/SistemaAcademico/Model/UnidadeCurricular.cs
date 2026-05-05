using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAcademico.Model
{
    public class UnidadeCurricular
    {
        public String Nome {  get; set; }
        public List<Estudante> Estudantes { get; set; }
        public List<Avaliacao> Avaliacoes { get; set; }

        public UnidadeCurricular(string nome)
        {
           this.Nome = nome;
           this.Estudantes = new List<Estudante>();
           this.Avaliacoes = new List<Avaliacao>();
        }

        public double CalcularNotaFinal() 
        {
            return Avaliacoes.Sum(a => a.CalcularNotaFinal());
        }

        public void EmitirPauta()
        {
            Console.WriteLine("\nPauta da Unidade Curricular");


            var listaOrdenada = Estudantes
                .Select(e => new { 
                Nome = e.Nome,
                Nota = CalcularNotaFinal()
                })
                .OrderByDescending(x => x.Nota);

            foreach ( var item in listaOrdenada)
            {
                Console.WriteLine($"{item.Nome} Nota Final : {item.Nota:F2}");
            }
        }
    }
}

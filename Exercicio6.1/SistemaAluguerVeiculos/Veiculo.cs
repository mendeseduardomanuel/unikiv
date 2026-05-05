using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAluguerVeiculos
{
    public class Veiculo
    {
        private string matricula;
        private string marca;
        private string modelo;
        private int ano;
        private double quilometragem;
        private bool disponivel;

        public string Matricula { get => matricula; set => matricula = value; }
        public string Marca { get => marca; set => marca = value; }
        public string Modelo { get => modelo; set => modelo = value; }
        public int Ano { get => ano; set => ano = value; }
        public double Quilometragem { get => quilometragem; set => quilometragem = value; }
        public bool Disponivel { get => disponivel; set => disponivel = value; }

        public Veiculo(string m, string ma, string mo, int a, double km)
        {
            matricula = m;
            marca = ma;
            modelo = mo;
            ano = a;
            quilometragem = km;
            disponivel = true;
        }

        public void AtualizarKm(double km)
        {
            if (km > 0) quilometragem += km;
        }

        public void Mostrar()
        {
            Console.WriteLine($"{matricula} | {marca} {modelo} | KM: {quilometragem} | {(disponivel ? "Livre" : "Alugado")}");
        }
    }

}

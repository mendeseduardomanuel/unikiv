using System;
using System.Collections.Generic;
using System.Text;

namespace SistemaAluguerVeiculos
{
    public class Aluguer
    {
        
        public Veiculo Veiculo { get; set; }
        public Cliente Cliente { get; set; }

        public double KmInicial { get; set; }
        public double KmFinal { get; set; }

        public bool Activo { get; set; }

        public Aluguer(Veiculo veiculo, Cliente cliente)
        {
            Veiculo = veiculo;
            Cliente = cliente;
            KmInicial = veiculo.Quilometragem; 
            KmFinal = 0;
            Activo = true;
        }

        public void Finalizar(double kmPercorridos)
        {
            if (kmPercorridos <= 0)
            {
                Console.WriteLine("Quilometragem inválida!");
                return;
            }

            KmFinal = KmInicial + kmPercorridos;

            Veiculo.AtualizarKm(kmPercorridos);
            Veiculo.Disponivel = true;

            Activo = false;
        }

        public void Mostrar()
        {
            Console.WriteLine("\n===== ALUGUER =====");
            Console.WriteLine($"Cliente: {Cliente.Nome}");
            Console.WriteLine($"Veículo: {Veiculo.Matricula}");
            Console.WriteLine($"KM Inicial: {KmInicial}");
            Console.WriteLine($"KM Final: {(Activo ? "Em uso" : KmFinal.ToString())}");
            Console.WriteLine($"Estado: {(Activo ? "Ativo" : "Finalizado")}");
        }
    }
}

using System;
using System.Collections.Generic;
using System.Linq;
namespace SistemaAluguerVeiculos
{
    public class Program
    {
        static List<Veiculo> veiculos = new List<Veiculo>();
        static List<Cliente> clientes = new List<Cliente>();
        static List<Aluguer> alugueres = new List<Aluguer>();
        static void Main(string[] args)
        {
            int opcao;

            do
            {
                Console.Clear();
                Console.WriteLine("=====  SISTEMA DE ALUGUER =====");
                Console.WriteLine("1 - Cadastrar Veículo");
                Console.WriteLine("2 - Cadastrar Cliente");
                Console.WriteLine("3 - Alugar Veículo");
                Console.WriteLine("4 - Devolver Veículo");
                Console.WriteLine("5 - Listar Veículos");
                Console.WriteLine("6 - Listar Alugueres");
                Console.WriteLine("0 - Sair");

                Console.Write("Opção: ");
                opcao = int.Parse(Console.ReadLine());

                switch (opcao)
                {
                    case 1: CadastrarVeiculo(); break;
                    case 2: CadastrarCliente(); break;
                    case 3: AlugarVeiculo(); break;
                    case 4: DevolverVeiculo(); break;
                    case 5: ListarVeiculos(); break;
                    case 6: ListarAlugueres(); break;
                }

            } while (opcao != 0);
        }

        
        static void Pausar()
        {
            Console.WriteLine("\nPressione qualquer tecla...");
            Console.ReadKey();
        }

        
        static void CadastrarVeiculo()
        {
            Console.Clear();

            Console.Write("Matrícula: ");
            string m = Console.ReadLine();

            Console.Write("Marca: ");
            string ma = Console.ReadLine();

            Console.Write("Modelo: ");
            string mo = Console.ReadLine();

            Console.Write("Ano: ");
            int a = int.Parse(Console.ReadLine());

            Console.Write("Quilometragem: ");
            double km = double.Parse(Console.ReadLine());

            veiculos.Add(new Veiculo(m, ma, mo, a, km));

            Console.WriteLine("Veículo cadastrado!");
            Pausar();
        }

        
        static void CadastrarCliente()
        {
            Console.Clear();

            Console.Write("Nome: ");
            string nome = Console.ReadLine();

            Console.Write("BI: ");
            string bi = Console.ReadLine();

            clientes.Add(new Cliente(nome, bi));

            Console.WriteLine("Cliente cadastrado!");
            Pausar();
        }

       
        static void AlugarVeiculo()
        {
            Console.Clear();

            var livres = veiculos.Where(v => v.Disponivel).ToList();

            if (livres.Count == 0)
            {
                Console.WriteLine("Nenhum veículo disponível.");
                Pausar();
                return;
            }

            Console.WriteLine("Escolha veículo:");
            for (int i = 0; i < livres.Count; i++)
                Console.WriteLine($"{i} - {livres[i].Matricula}");

            int vIndex = int.Parse(Console.ReadLine());

            Console.WriteLine("Escolha cliente:");
            for (int i = 0; i < clientes.Count; i++)
                Console.WriteLine($"{i} - {clientes[i].Nome}");

            int cIndex = int.Parse(Console.ReadLine());

            var aluguer = new Aluguer(livres[vIndex], clientes[cIndex]);

            livres[vIndex].Disponivel = false;
            alugueres.Add(aluguer);

            Console.WriteLine("Veículo alugado!");
            Pausar();
        }

       
        static void DevolverVeiculo()
        {
            Console.Clear();

            var activos = alugueres.Where(a => a.Activo).ToList();

            if (activos.Count == 0)
            {
                Console.WriteLine("⚠️ Nenhum aluguer ativo.");
                Pausar();
                return;
            }

            Console.WriteLine("Escolha aluguer:");
            for (int i = 0; i < activos.Count; i++)
                Console.WriteLine($"{i} - {activos[i].Veiculo.Matricula} ({activos[i].Cliente.Nome})");

            int index = int.Parse(Console.ReadLine());

            Console.Write("KM percorridos: ");
            double km = double.Parse(Console.ReadLine());

            activos[index].Finalizar(km);

            Console.WriteLine("Veículo devolvido!");
            Pausar();
        }

      
        static void ListarVeiculos()
        {
            Console.Clear();

            foreach (var v in veiculos)
                v.Mostrar();

            Pausar();
        }

        
        static void ListarAlugueres()
        {
            Console.Clear();

            foreach (var a in alugueres)
            {
                Console.WriteLine($"{a.Cliente.Nome} -> {a.Veiculo.Matricula} | {(a.Activo ? "Ativo" : "Finalizado")}");
            }

            Pausar();
        }
    }
}

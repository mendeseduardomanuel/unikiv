using System;
using System.Collections.Generic;
using Sistema_de_Gestao_de_Veiculos.Model;

namespace Sistema_de_Gestao_de_Veiculos
{
    class Program
    {
        static List<Veiculo> veiculos = new List<Veiculo>();
        static List<Reserva> reservas = new List<Reserva>();
        static int reservaId = 1;

        static void Main()
        {
            while (true)
            {
                Console.Clear();
                Console.WriteLine("=== Sistema de Gestão de Veículos ===");
                Console.WriteLine("1. Adicionar Veículo");
                Console.WriteLine("2. Listar Veículos");
                Console.WriteLine("3. Criar Reserva");
                Console.WriteLine("4. Listar Reservas");
                Console.WriteLine("0. Sair");
                Console.Write("Escolha uma opção: ");

                string opcao = Console.ReadLine();

                switch (opcao)
                {
                    case "1": AdicionarVeiculo(); break;
                    case "2": ListarVeiculos(); break;
                    case "3": CriarReserva(); break;
                    case "4": ListarReservas(); break;
                    case "0": return;
                    default: Console.WriteLine("Opção inválida!"); Pause(); break;
                }
            }
        }

        static void AdicionarVeiculo()
        {
            Console.Write("Tipo (1-Automóvel, 2-Motociclo, 3-Camião): ");
            string tipo = Console.ReadLine();

            Veiculo v = null;
            if (tipo == "1")
            {
                v = new Automovel();
                Console.Write("Número de portas: "); ((Automovel)v).NumPortas = int.Parse(Console.ReadLine());
                Console.Write("Tipo combustível: "); ((Automovel)v).TipoCombustivel = Console.ReadLine();
                Console.Write("Número de passageiros: "); ((Automovel)v).NumPassageiros = int.Parse(Console.ReadLine());
            }
            else if (tipo == "2")
            {
                v = new Motociclo();
                Console.Write("Cilindrada: "); ((Motociclo)v).Cilindrada = int.Parse(Console.ReadLine());
                Console.Write("Tem SideCar (true/false): "); ((Motociclo)v).TemSideCar = bool.Parse(Console.ReadLine());
            }
            else if (tipo == "3")
            {
                v = new Camiao();
                Console.Write("Capacidade carga (t): "); ((Camiao)v).CapacidadeCarga = double.Parse(Console.ReadLine());
                Console.Write("Número de eixos: "); ((Camiao)v).NumEixos = int.Parse(Console.ReadLine());
            }
            else { Console.WriteLine("Tipo inválido!"); Pause(); return; }

            Console.Write("Matrícula: "); v.Matricula = Console.ReadLine();
            Console.Write("Marca: "); v.Marca = Console.ReadLine();
            Console.Write("Modelo: "); v.Modelo = Console.ReadLine();
            Console.Write("Ano: "); v.Ano = int.Parse(Console.ReadLine());

            veiculos.Add(v);
            Console.WriteLine("Veículo adicionado com sucesso!");
            Pause();
        }

        static void ListarVeiculos()
        {
            Console.WriteLine("=== Lista de Veículos ===");
            foreach (var v in veiculos)
            {
                Console.WriteLine($"{v.GetTipo()} - {v.Matricula} - {v.Marca} {v.Modelo} - Estado: {v.Estado}");
            }
            Pause();
        }

        static void CriarReserva()
        {
            if (veiculos.Count == 0) { Console.WriteLine("Não há veículos disponíveis."); Pause(); return; }

            Console.Write("Nome do cliente: ");
            Cliente c = new Cliente { Nome = Console.ReadLine() };

            Console.WriteLine("Escolha o veículo:");
            for (int i = 0; i < veiculos.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {veiculos[i].GetTipo()} - {veiculos[i].Matricula}");
            }

            int escolha = int.Parse(Console.ReadLine()) - 1;
            if (escolha < 0 || escolha >= veiculos.Count) { Console.WriteLine("Escolha inválida!"); Pause(); return; }

            Veiculo v = veiculos[escolha];

            Console.Write("Data início (yyyy-mm-dd): "); DateTime inicio = DateTime.Parse(Console.ReadLine());
            Console.Write("Data fim (yyyy-mm-dd): "); DateTime fim = DateTime.Parse(Console.ReadLine());

            Reserva r = new Reserva
            {
                Id = reservaId++,
                Cliente = c,
                Veiculo = v,
                DataInicio = inicio,
                DataFim = fim,
                ValorTotal = v.CalcularValorDiaria() * (fim - inicio).Days
            };
            reservas.Add(r);
            v.Estado = EstadoVeiculo.RESERVADO;

            Console.WriteLine("Reserva criada com sucesso!");
            Pause();
        }

        static void ListarReservas()
        {
            Console.WriteLine("=== Reservas ===");
            foreach (var r in reservas)
            {
                Console.WriteLine($"ID: {r.Id} - Cliente: {r.Cliente.Nome} - Veículo: {r.Veiculo.Matricula} - {r.DataInicio:dd/MM/yyyy} a {r.DataFim:dd/MM/yyyy} - Valor: {r.ValorTotal} Kz");
            }
            Pause();
        }

        static void Pause()
        {
            Console.WriteLine("Pressione Enter para continuar...");
            Console.ReadLine();
        }
    }
}

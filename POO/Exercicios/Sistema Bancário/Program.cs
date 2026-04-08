using Sistema_Bancário.Model;

namespace Sistema_Bancário
{
    public class Program
    {
        static List<Cliente> clientes = new List<Cliente>();
        static List<ContaBancaria> contas = new List<ContaBancaria>();

        static void Main(string[] args)
        {
            bool sair = false;
            while (!sair)
            {
                Console.Clear();
                Console.WriteLine("=== SISTEMA BANCÁRIO ===");
                Console.WriteLine("1. Criar Cliente");
                Console.WriteLine("2. Criar Conta");
                Console.WriteLine("3. Depositar");
                Console.WriteLine("4. Levantar");
                Console.WriteLine("5. Ver Saldo");
                Console.WriteLine("6. Ver Histórico");
                Console.WriteLine("0. Sair");
                Console.Write("Escolha uma opção: ");

                string opcao = Console.ReadLine();
                switch (opcao)
                {
                    case "1":
                        CriarCliente();
                        break;
                    case "2":
                        CriarConta();
                        break;
                    case "3":
                        Depositar();
                        break;
                    case "4":
                        Levantar();
                        break;
                    case "5":
                        VerSaldo();
                        break;
                    case "6":
                        VerHistorico();
                        break;
                    case "0":
                        sair = true;
                        break;
                    default:
                        Console.WriteLine("Opção inválida!");
                        Pausa();
                        break;
                }
            }
        }

        static void CriarCliente()
        {
            Console.Write("Nome do cliente: ");
            string nome = Console.ReadLine();
            Console.Write("NIF: ");
            string nif = Console.ReadLine();
            Console.Write("Telefone: ");
            string telefone = Console.ReadLine();
            Console.Write("Email: ");
            string email = Console.ReadLine();

            Cliente c = new Cliente
            {
                Id = clientes.Count + 1,
                Nome = nome,
                Nif = nif,
                Telefone = telefone,
                Email = email
            };
            clientes.Add(c);

            Console.WriteLine("Cliente criado com sucesso!");
            Pausa();
        }

        static void CriarConta()
        {
            if (clientes.Count == 0)
            {
                Console.WriteLine("Não há clientes cadastrados!");
                Pausa();
                return;
            }

            Console.WriteLine("Escolha o cliente (ID): ");
            foreach (var c in clientes)
                Console.WriteLine($"{c.Id} - {c.Nome}");
            int idCliente = int.Parse(Console.ReadLine());
            Cliente cliente = clientes.Find(x => x.Id == idCliente);

            Console.WriteLine("Tipo de Conta:");
            Console.WriteLine("1. Conta Ordem");
            Console.WriteLine("2. Conta Poupança");
            Console.WriteLine("3. Conta Corrente");
            string tipo = Console.ReadLine();

            ContaBancaria conta = tipo switch
            {
                "1" => new ContaOrdem { Titular = cliente, Iban = "IBAN" + contas.Count },
                "2" => new ContaPoupanca { Titular = cliente, Iban = "IBAN" + contas.Count, TaxaJuroAnual = 0.05 },
                "3" => new ContaCorrente { Titular = cliente, Iban = "IBAN" + contas.Count, LimiteCredito = 1000, ComissaoMensal = 10 },
                _ => null
            };

            if (conta != null)
            {
                contas.Add(conta);
                cliente.Contas.Add(conta);
                Console.WriteLine("Conta criada com sucesso!");
            }
            Pausa();
        }

        static ContaBancaria SelecionarConta()
        {
            if (contas.Count == 0)
            {
                Console.WriteLine("Não há contas cadastradas!");
                Pausa();
                return null;
            }

            Console.WriteLine("Escolha a conta (IBAN): ");
            foreach (var c in contas)
                Console.WriteLine($"{c.Iban} - {c.Titular.Nome}");
            string iban = Console.ReadLine();
            return contas.Find(c => c.Iban == iban);
        }

        static void Depositar()
        {
            var conta = SelecionarConta();
            if (conta == null) return;

            Console.Write("Valor a depositar: ");
            double valor = double.Parse(Console.ReadLine());
            conta.Depositar(valor);

            if (conta is IAuditavel aud)
                aud.RegistarAuditoria($"Depósito: {valor} Kz em {DateTime.Now}");

            Console.WriteLine("Depósito realizado!");
            Pausa();
        }

        static void Levantar()
        {
            var conta = SelecionarConta();
            if (conta == null) return;

            Console.Write("Valor a levantar: ");
            double valor = double.Parse(Console.ReadLine());
            bool sucesso = conta.Levantar(valor);

            if (sucesso)
            {
                if (conta is IAuditavel aud)
                    aud.RegistarAuditoria($"Levantamento: {valor} Kz em {DateTime.Now}");
                Console.WriteLine("Levantamento realizado!");
            }
            else
            {
                Console.WriteLine("Saldo insuficiente!");
            }
            Pausa();
        }

        static void VerSaldo()
        {
            var conta = SelecionarConta();
            if (conta == null) return;

            Console.WriteLine($"Saldo atual: {conta.GetSaldo()} Kz");
            Pausa();
        }

        static void VerHistorico()
        {
            var conta = SelecionarConta();
            if (conta == null) return;

            if (conta is IAuditavel aud)
            {
                Console.WriteLine("Histórico de operações:");
                foreach (var log in aud.ObterLog())
                    Console.WriteLine(log);
            }
            Pausa();
        }

        static void Pausa()
        {
            Console.WriteLine("Pressione ENTER para continuar...");
            Console.ReadLine();
        }
    }
}
